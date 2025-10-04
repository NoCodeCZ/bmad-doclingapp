from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    status: str


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    ocr_enabled: bool = False,
    processing_mode: str = "fast"
):
    """Upload a document for processing."""
    # TODO: Implement file upload logic
    return DocumentUploadResponse(
        id="placeholder-id",
        filename=file.filename,
        status="queued"
    )