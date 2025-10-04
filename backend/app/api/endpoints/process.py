from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.processing_service import processing_service
from app.services.supabase_service import supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/process/{document_id}")
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks
):
    """Trigger document processing for an uploaded document."""
    try:
        # Get document from database
        document = await supabase_service.get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        if document['status'] != 'queued':
            raise HTTPException(
                status_code=400,
                detail=f"Document cannot be processed. Current status: {document['status']}"
            )

        # Start background processing
        background_tasks.add_task(
            processing_service.process_document_async,
            document_id=document_id,
            filename=document['filename'],
            processing_options=document.get('processing_options', {})
        )

        return {
            "message": "Document processing started",
            "document_id": document_id,
            "status": "processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting document processing for {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )