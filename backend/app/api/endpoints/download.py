from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.supabase_service import supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/download/{document_id}")
async def download_document(document_id: str):
    """Download a processed document."""
    try:
        # Get document from database
        document = await supabase_service.get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        if document['status'] != 'complete':
            raise HTTPException(
                status_code=400,
                detail=f"Document is not ready for download. Status: {document['status']}"
            )

        # Construct processed file path
        original_filename = document['filename']
        base_name = original_filename.rsplit('.', 1)[0]  # Remove extension
        processed_filename = f"{base_name}.md"
        file_path = f"{document_id}/{processed_filename}"

        # Download file from Supabase storage
        file_content = await supabase_service.download_file(
            bucket="processed",
            file_path=file_path
        )

        # Return file as streaming response
        return StreamingResponse(
            iter([file_content]),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={processed_filename}",
                "Content-Length": str(len(file_content))
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during download"
        )