"""
Pydantic models for request/response validation and database schemas.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status enum."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class ProcessingMode(str, Enum):
    """Processing mode enum."""
    FAST = "fast"
    QUALITY = "quality"


class ProcessingOptions(BaseModel):
    """Processing options for document conversion."""
    ocr_enabled: bool = False
    processing_mode: ProcessingMode = ProcessingMode.FAST

    class Config:
        use_enum_values = True


class DocumentUpload(BaseModel):
    """Document upload request model."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0, le=10485760)  # 10MB max
    processing_options: ProcessingOptions

    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename has allowed extension."""
        allowed_extensions = ['.pdf', '.docx', '.pptx', '.xlsx']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'Filename must end with one of: {", ".join(allowed_extensions)}')
        return v


class DocumentCreate(BaseModel):
    """Document creation model for database."""
    filename: str
    status: DocumentStatus = DocumentStatus.QUEUED
    processing_options: Dict[str, Any]
    file_size: Optional[int] = None
    content_type: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Document update model for database."""
    status: Optional[DocumentStatus] = None
    processing_options: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    processed_file_path: Optional[str] = None
    original_file_path: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str
    filename: str
    status: DocumentStatus
    processing_options: ProcessingOptions
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    """Document status response model with additional metadata."""
    id: str
    filename: str
    status: DocumentStatus
    processing_options: ProcessingOptions
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_stage: Optional[str] = None
    elapsed_time: Optional[int] = None
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentStats(BaseModel):
    """Document statistics model."""
    status: DocumentStatus
    count: int
    avg_processing_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """File upload response model."""
    id: str
    filename: str
    status: DocumentStatus
    message: str = "File uploaded successfully"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime
    version: str
    database_connected: bool
    storage_connected: bool


class ProcessingProgress(BaseModel):
    """Processing progress model."""
    stage: str
    percentage: int = Field(..., ge=0, le=100)
    message: str
    estimated_time_remaining: Optional[int] = None  # seconds


class DownloadRequest(BaseModel):
    """Download request model."""
    document_id: str


class DownloadResponse(BaseModel):
    """Download response model."""
    url: str
    filename: str
    expires_in: int = 3600  # seconds


# Storage bucket models
class StorageBucket(BaseModel):
    """Storage bucket model."""
    id: str
    name: str
    public: bool
    file_size_limit: int
    allowed_mime_types: List[str]

    class Config:
        from_attributes = True


class StorageObject(BaseModel):
    """Storage object model."""
    id: str
    bucket_id: str
    name: str
    owner: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# Validation helpers
class FileValidationMixin:
    """Mixin for file validation methods."""
    
    @staticmethod
    def is_valid_file_type(filename: str, content_type: str) -> bool:
        """Check if file type is allowed."""
        allowed_types = {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        }
        
        if content_type not in allowed_types:
            return False
        
        allowed_extensions = allowed_types[content_type]
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
    
    @staticmethod
    def is_valid_file_size(file_size: int, max_size: int = 10485760) -> bool:
        """Check if file size is within limits."""
        return 0 < file_size <= max_size


# Database query models
class DocumentQuery(BaseModel):
    """Document query parameters."""
    status: Optional[DocumentStatus] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="created_at", pattern="^(created_at|completed_at|filename)$")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$")


class BatchOperation(BaseModel):
    """Batch operation model."""
    document_ids: List[str] = Field(..., min_items=1, max_items=50)
    operation: str = Field(..., pattern="^(delete|retry)$")