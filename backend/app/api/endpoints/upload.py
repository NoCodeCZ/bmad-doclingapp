from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from app.models.schemas import DocumentUpload, FileUploadResponse
from app.services.supabase_service import supabase_service
from app.services.processing_service import processing_service
from app.core.config import settings
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
    """Upload a document for processing."""
    try:
        # Validate file type
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )

        # Read file content
        file_content = await file.read()

        # Validate file size
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {len(file_content)} bytes. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )

        # Prepare processing options
        processing_options = {
            "ocr_enabled": ocr_enabled,
            "processing_mode": processing_mode
        }

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during file upload"
        )