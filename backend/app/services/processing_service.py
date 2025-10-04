"""
Document processing service using Docling.
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

logger = logging.getLogger(__name__)


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
        Process a document using Docling.

        Args:
            document_id: Unique document identifier
            filename: Original filename
            processing_options: Processing configuration

        Returns:
            Path to the processed markdown file

        Raises:
            Exception: If processing fails
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

                # Convert document
                result = converter.convert(temp_file_path)

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

                logger.info(f"Document {document_id} processed successfully")
                return output_path

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            # Update document status to failed
            error_message = f"Processing failed: {str(e)}"
            await supabase_service.update_document_status(
                document_id,
                'failed',
                error_message
            )
            logger.error(f"Document processing failed for {document_id}: {e}")
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