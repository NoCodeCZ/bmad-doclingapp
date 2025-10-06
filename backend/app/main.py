from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid

from app.api.endpoints import health, upload, process, status, download
from app.core.config import settings
from app.core.exceptions import DocumentProcessingError
from app.utils.logger import log_error

app = FastAPI(
    title="Workshop Document Processor API",
    description="API for converting office documents to AI-optimized markdown",
    version="1.0.0",
)

# Configure CORS
# Handle both "*" (allow all) and list of specific origins
allowed_origins = settings.ALLOWED_ORIGINS
if isinstance(allowed_origins, str):
    # If it's a string (like "*"), use it directly
    allowed_origins = [allowed_origins] if allowed_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if allowed_origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handler middleware
@app.exception_handler(DocumentProcessingError)
async def document_processing_exception_handler(
    request: Request, exc: DocumentProcessingError
):
    """
    Handle custom document processing errors.

    Implements AC 6: Backend service errors show user-friendly messages
    Implements AC 8: Error logging captures full error details
    """
    error_id = str(uuid.uuid4())

    # Log error with full context
    log_error(
        error_message=exc.message,
        error_code=exc.code,
        request_id=error_id,
        user_agent=request.headers.get("user-agent"),
        exception=exc,
        path=str(request.url.path),
        method=request.method,
    )

    # Return user-friendly error response
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat(),
                "requestId": error_id,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors with user-friendly messages.

    Implements AC 6: Backend service errors show user-friendly messages
    """
    error_id = str(uuid.uuid4())

    # Log error with full context
    log_error(
        error_message=str(exc),
        error_code="INTERNAL_ERROR",
        request_id=error_id,
        user_agent=request.headers.get("user-agent"),
        exception=exc,
        path=str(request.url.path),
        method=request.method,
    )

    # Return generic user-friendly error
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred - please try again.",
                "timestamp": datetime.utcnow().isoformat(),
                "requestId": error_id,
            }
        },
    )

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(process.router, prefix="/api", tags=["process"])
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(download.router, prefix="/api", tags=["download"])


@app.get("/")
async def root():
    return {"message": "Workshop Document Processor API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )