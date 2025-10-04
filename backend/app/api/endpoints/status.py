from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DocumentStatus(BaseModel):
    id: str
    filename: str
    status: str
    progress: int = 0
    error_message: str = None


@router.get("/status/{document_id}", response_model=DocumentStatus)
async def get_document_status(document_id: str):
    """Get the processing status of a document."""
    # TODO: Implement status checking logic
    return DocumentStatus(
        id=document_id,
        filename="placeholder.pdf",
        status="queued"
    )