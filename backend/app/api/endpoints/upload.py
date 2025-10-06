from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from app.models.schemas import DocumentUpload, FileUploadResponse
from app.services.supabase_service import supabase_service
from app.services.processing_service import processing_service
from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    UnsupportedFileFormatError,
    SupabaseError,
)
from app.utils.logger import log_error
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ocr_enabled: bool = False,
    processing_mode: str = "fast"
):
    """
    Upload a document for processing.

    Implements AC 2: File validation errors show specific guidance
    Implements AC 3: Unsupported format errors include allowed formats
    Implements AC 6: Backend service errors show user-friendly messages
    """
    # Validate processing mode
    if processing_mode not in ["fast", "quality"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid processing mode: {processing_mode}. Must be 'fast' or 'quality'"
        )

    # Read file content
    file_content = await file.read()

    # Validate file size (AC 2)
    if len(file_content) > settings.MAX_FILE_SIZE:
        file_size_mb = len(file_content) / (1024 * 1024)
        raise FileTooLargeError(file_size_mb=file_size_mb)

    # Validate file type (AC 3)
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise UnsupportedFileFormatError(file_extension=file_extension)

    # Prepare processing options
    processing_options = {
        "ocr_enabled": ocr_enabled,
        "processing_mode": processing_mode
    }

    try:
        # Create document record in database
        doc_id = await supabase_service.create_document_record(
            filename=file.filename,
            processing_options=processing_options
        )

        # Upload file to Supabase storage
        file_path = f"{doc_id}/{file.filename}"
        await supabase_service.upload_file(
            bucket="uploads",
            file_path=file_path,
            file_content=file_content,
            content_type=file.content_type
        )

        # Start background processing
        background_tasks.add_task(
            processing_service.process_document_async,
            document_id=doc_id,
            filename=file.filename,
            processing_options=processing_options
        )

        logger.info(f"Document uploaded successfully: {doc_id}, file: {file.filename}")

        return FileUploadResponse(
            id=doc_id,
            filename=file.filename,
            status="queued"
        )

    except Exception as e:
        # Log Supabase errors with context (AC 6)
        log_error(
            error_message=f"Upload service error: {str(e)}",
            error_code="UPLOAD_ERROR",
            file_metadata={
                "name": file.filename,
                "size": len(file_content),
                "type": file.content_type,
            },
            exception=e,
        )
        raise SupabaseError(details=str(e))