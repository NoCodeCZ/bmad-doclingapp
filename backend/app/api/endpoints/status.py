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

        # Calculate elapsed time if processing started
        elapsed_time = None
        if document.get('created_at'):
            from datetime import datetime
            created_at = datetime.fromisoformat(document['created_at'].replace('Z', '+00:00'))
            elapsed_time = int((datetime.now(created_at.tzinfo) - created_at).total_seconds())

        # Get processing options
        processing_options = document.get('processing_options', {})

        # Calculate progress based on status, elapsed time, and processing options
        progress = _calculate_progress(
            status=document['status'],
            elapsed_time=elapsed_time,
            processing_options=processing_options
        )

        # Get detailed progress stage
        progress_stage = _get_progress_stage(
            status=document['status'],
            elapsed_time=elapsed_time
        )

        # Generate download URL for completed documents
        download_url = None
        if document['status'] == 'complete':
            try:
                download_url = await supabase_service.get_file_url(
                    bucket="processed",
                    file_path=f"{document_id}/{document['filename'].rsplit('.', 1)[0]}.md"
                )
            except Exception as e:
                logger.warning(f"Could not generate download URL for {document_id}: {e}")

        return DocumentStatusResponse(
            id=document['id'],
            filename=document['filename'],
            status=document['status'],
            processing_options=processing_options,
            created_at=document['created_at'],
            completed_at=document.get('completed_at'),
            error_message=document.get('error_message'),
            progress_stage=progress_stage,
            elapsed_time=elapsed_time,
            download_url=download_url,
            progress=progress
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status for {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


def _get_progress_stage(status: str, elapsed_time: int = None) -> str:
    """
    Get detailed progress stage from status and elapsed time.

    Stages:
    - Uploading file... (queued < 5 seconds)
    - Queued for processing (queued >= 5 seconds)
    - Converting document (processing < 100 seconds)
    - Finalizing... (processing >= 100 seconds)
    - Processing complete (complete)
    - Processing failed (failed)
    """
    # Add uploading stage for very recent documents
    if status == 'queued' and (elapsed_time or 0) < 5:
        return 'Uploading file...'

    # Add finalizing stage for long-running processing
    if status == 'processing' and (elapsed_time or 0) > 100:
        return 'Finalizing...'

    stages = {
        'queued': 'Queued for processing',
        'processing': 'Converting document',
        'complete': 'Processing complete',
        'failed': 'Processing failed'
    }

    return stages.get(status, 'Unknown')


def _calculate_progress(status: str, elapsed_time: int = None, processing_options: dict = None) -> int:
    """
    Calculate progress percentage based on status and elapsed time.

    Progress ranges:
    - queued: 0-10% based on elapsed time
    - processing: 10-95% based on estimated total time
    - complete: 100%
    - failed: 0%
    """
    if status == 'complete':
        return 100
    elif status == 'failed':
        return 0
    elif status == 'queued':
        return min(elapsed_time or 0, 10)  # 0-10% for queued
    elif status == 'processing':
        # Estimate based on processing mode and elapsed time
        processing_options = processing_options or {}
        base_time = 30 if processing_options.get('mode') == 'fast' else 90
        ocr_enabled = processing_options.get('ocr_enabled', False)
        ocr_multiplier = 2 if ocr_enabled else 1
        estimated_total = base_time * ocr_multiplier

        # Calculate progress: 10% base + up to 80% based on time
        if elapsed_time:
            progress = 10 + min((elapsed_time / estimated_total) * 80, 80)
            return min(int(progress), 95)  # Cap at 95% until complete
        return 10
    return 0