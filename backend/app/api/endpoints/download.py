from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/download/{document_id}")
async def download_document(document_id: str):
    """Download a processed document."""
    # TODO: Implement download logic
    raise HTTPException(
        status_code=404,
        detail="Document not found or not processed yet"
    )