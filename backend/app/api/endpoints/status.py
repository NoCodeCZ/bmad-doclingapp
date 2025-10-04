from fastapi import APIRouter, HTTPException
from app.models.schemas import DocumentStatusResponse
from app.services.supabase_service import supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str):
    """Get the processing status of a document."""
    try:
        # Get document from database
        document = await supabase_service.get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        # Calculate progress based on status
        progress = 0
        elapsed_time = None
        download_url = None

        if document['status'] == 'processing':
            progress = 50  # Mid-point for processing
        elif document['status'] == 'complete':
            progress = 100
            # Generate download URL for completed documents
            try:
                download_url = await supabase_service.get_file_url(
                    bucket="processed",
                    file_path=f"{document_id}/{document['filename'].rsplit('.', 1)[0]}.md"
                )
            except Exception as e:
                logger.warning(f"Could not generate download URL for {document_id}: {e}")

        # Calculate elapsed time if processing started
        if document.get('created_at'):
            from datetime import datetime
            created_at = datetime.fromisoformat(document['created_at'].replace('Z', '+00:00'))
            elapsed_time = int((datetime.now(created_at.tzinfo) - created_at).total_seconds())

        return DocumentStatusResponse(
            id=document['id'],
            filename=document['filename'],
            status=document['status'],
            processing_options=document.get('processing_options', {}),
            created_at=document['created_at'],
            completed_at=document.get('completed_at'),
            error_message=document.get('error_message'),
            progress_stage=_get_progress_stage(document['status']),
            elapsed_time=elapsed_time,
            download_url=download_url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status for {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


def _get_progress_stage(status: str) -> str:
    """Get human-readable progress stage from status."""
    stages = {
        'queued': 'Queued for processing',
        'processing': 'Converting document',
        'complete': 'Processing complete',
        'failed': 'Processing failed'
    }
    return stages.get(status, 'Unknown')