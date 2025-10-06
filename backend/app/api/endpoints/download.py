from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.supabase_service import supabase_service
from app.utils.filename_utils import get_safe_filename
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/download/{document_id}")
async def download_document(document_id: str):
    """
    Download a processed document.

    Implements AC 6: Stream file from Supabase with proper MIME type and headers
    Implements AC 3: Clean filename with extension replacement and special char removal
    Implements AC 7: User-friendly error messages for download failures
    """
    try:
        # Get document from database
        document = await supabase_service.get_document(document_id)

        if not document:
            logger.warning(f"Document not found: {document_id}")
            raise HTTPException(
                status_code=404,
                detail="Download failed - file may have been moved or deleted. Please process document again."
            )

        if document['status'] != 'complete':
            logger.warning(f"Document not ready for download: {document_id}, status: {document['status']}")
            raise HTTPException(
                status_code=400,
                detail=f"Document is not ready for download. Current status: {document['status']}. Please wait for processing to complete."
            )

        # Clean filename for safe download (AC3)
        original_filename = document['filename']
        cleaned_filename = get_safe_filename(original_filename, fallback="document.md")

        # Construct processed file path using original structure
        base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        processed_filename = f"{base_name}.md"
        file_path = f"{document_id}/{processed_filename}"

        # Download file from Supabase storage
        try:
            file_content = await supabase_service.download_file(
                bucket="processed",
                file_path=file_path
            )
        except Exception as storage_error:
            logger.error(f"Storage error downloading {document_id}: {storage_error}")
            raise HTTPException(
                status_code=500,
                detail="Download failed - file may have been moved or deleted. Please process document again."
            )

        # Calculate file size for logging (AC4 handled in frontend)
        file_size = len(file_content)
        logger.info(f"Downloading document {document_id}: {cleaned_filename} ({file_size} bytes)")

        # Return file as streaming response with proper headers (AC2, AC6)
        return StreamingResponse(
            iter([file_content]),
            media_type="text/markdown",
            headers={
                # AC2: Proper content-disposition header for download (not browser display)
                "Content-Disposition": f'attachment; filename="{cleaned_filename}"',
                "Content-Length": str(file_size),
                # AC6: Proper MIME type
                "Content-Type": "text/markdown; charset=utf-8",
                # Security headers
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error downloading document {document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Download failed - an unexpected error occurred. Please try again or contact support if the problem persists."
        )