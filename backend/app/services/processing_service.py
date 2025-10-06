"""
Document processing service using Docling.

Implements AC 4: Processing timeout error handling
Implements AC 5: Corrupted file detection and handling
"""
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import logging

from app.services.supabase_service import supabase_service
from app.core.exceptions import (
    ProcessingTimeoutError,
    CorruptedFileError,
    DoclingProcessingError,
)
from app.utils.logger import log_error, log_info

logger = logging.getLogger(__name__)

# Processing timeout in seconds (5 minutes)
PROCESSING_TIMEOUT = 300


class ProcessingService:
    """Service for processing documents with Docling."""

    def __init__(self):
        """Initialize the processing service."""
        self.converter = DocumentConverter()

    async def process_document(
        self,
        document_id: str,
        filename: str,
        processing_options: Dict[str, Any]
    ) -> str:
        """
        Process a document using Docling with timeout and error handling.

        Args:
            document_id: Unique document identifier
            filename: Original filename
            processing_options: Processing configuration

        Returns:
            Path to the processed markdown file

        Raises:
            ProcessingTimeoutError: If processing takes longer than timeout
            CorruptedFileError: If file is corrupted or password-protected
            DoclingProcessingError: If Docling processing fails
        """
        try:
            # Update status to processing
            await supabase_service.update_document_status(document_id, 'processing')

            # Download file from uploads bucket
            file_path = f"{document_id}/{filename}"
            file_content = await supabase_service.download_file("uploads", file_path)

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # Wrap processing in timeout (AC 4)
                try:
                    result_path = await asyncio.wait_for(
                        self._process_with_docling(
                            temp_file_path,
                            document_id,
                            filename,
                            processing_options
                        ),
                        timeout=PROCESSING_TIMEOUT
                    )
                    return result_path

                except asyncio.TimeoutError:
                    # Processing timeout error (AC 4)
                    log_error(
                        error_message="Processing timeout",
                        error_code="PROCESSING_TIMEOUT",
                        document_id=document_id,
                        file_metadata={
                            "name": filename,
                            "size": len(file_content),
                        },
                        processing_options=processing_options,
                    )
                    await supabase_service.update_document_status(
                        document_id,
                        'failed',
                        'Processing timeout'
                    )
                    raise ProcessingTimeoutError()

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except ProcessingTimeoutError:
            raise
        except CorruptedFileError:
            raise
        except DoclingProcessingError:
            raise
        except Exception as e:
            # Update document status to failed
            error_message = f"Processing failed: {str(e)}"
            await supabase_service.update_document_status(
                document_id,
                'failed',
                error_message
            )

            # Log error with context
            log_error(
                error_message=error_message,
                error_code="PROCESSING_ERROR",
                document_id=document_id,
                exception=e,
            )

            raise DoclingProcessingError(details=str(e))

    async def _process_with_docling(
        self,
        temp_file_path: str,
        document_id: str,
        filename: str,
        processing_options: Dict[str, Any]
    ) -> str:
        """
        Internal method to process document with Docling.

        Implements AC 5: Corrupted file detection and handling
        """
        try:
            # Configure Docling options
            ocr_enabled = processing_options.get('ocr_enabled', False)
            processing_mode = processing_options.get('processing_mode', 'fast')

            # Set up pipeline options based on processing mode
            if processing_mode == 'quality':
                # Quality mode: full analysis with OCR if enabled
                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = ocr_enabled
                pipeline_options.do_table_structure = True
            else:
                # Fast mode: basic extraction, OCR only if explicitly enabled
                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = ocr_enabled
                pipeline_options.do_table_structure = False

            # Configure converter with options
            converter = DocumentConverter(
                format_options={
                    "pipeline_options": pipeline_options
                }
            )

            # Convert document (AC 5: Detect corrupted files)
            try:
                result = converter.convert(temp_file_path)
            except Exception as conv_error:
                # Check for common corruption/protection indicators
                error_str = str(conv_error).lower()
                if any(indicator in error_str for indicator in [
                    'password',
                    'encrypted',
                    'protected',
                    'corrupt',
                    'damaged',
                    'invalid',
                ]):
                    log_error(
                        error_message="Corrupted or protected file",
                        error_code="CORRUPTED_FILE",
                        document_id=document_id,
                        exception=conv_error,
                    )
                    raise CorruptedFileError()
                raise

            # Extract markdown content
            markdown_content = result.document.export_to_markdown()

            # Generate output filename
            base_name = Path(filename).stem
            output_filename = f"{base_name}.md"
            output_path = f"{document_id}/{output_filename}"

            # Upload processed file to processed bucket
            await supabase_service.upload_file(
                bucket="processed",
                file_path=output_path,
                file_content=markdown_content.encode('utf-8'),
                content_type="text/markdown"
            )

            # Update document status to complete
            await supabase_service.update_document_status(document_id, 'complete')

            log_info(
                f"Document processed successfully",
                document_id=document_id,
            )

            return output_path

        except CorruptedFileError:
            raise
        except Exception as e:
            # Log Docling-specific errors
            log_error(
                error_message=f"Docling processing error: {str(e)}",
                error_code="DOCLING_ERROR",
                document_id=document_id,
                exception=e,
            )
            raise

    async def process_document_async(
        self,
        document_id: str,
        filename: str,
        processing_options: Dict[str, Any]
    ) -> None:
        """
        Process a document asynchronously in the background.

        This method should be called with asyncio.create_task() to run in background.
        """
        try:
            await self.process_document(document_id, filename, processing_options)
        except Exception as e:
            logger.error(f"Background processing failed for {document_id}: {e}")


# Global instance
processing_service = ProcessingService()