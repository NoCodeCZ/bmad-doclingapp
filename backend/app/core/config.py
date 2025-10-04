from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Workshop Document Processor"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://workshop-document-processor.ondigitalocean.app",
    ]
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # File processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
    ]
    
    # Processing
    PROCESSING_TIMEOUT: int = 300  # 5 minutes
    DEFAULT_OCR_ENABLED: bool = False
    DEFAULT_PROCESSING_MODE: str = "fast"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()