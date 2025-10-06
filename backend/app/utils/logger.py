"""
Structured error logging for document processing application.

Implements AC 8: Error logging captures full error details (stack trace, document ID, file metadata)
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

# Configure logger
logger = logging.getLogger(__name__)


def log_error(
    error_message: str,
    error_code: str,
    document_id: Optional[str] = None,
    file_metadata: Optional[Dict[str, Any]] = None,
    processing_options: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    exception: Optional[Exception] = None,
    **kwargs: Any,
) -> str:
    """
    Log error with structured context for debugging.

    Args:
        error_message: Human-readable error message
        error_code: Error code (e.g., FILE_TOO_LARGE, PROCESSING_TIMEOUT)
        document_id: Document ID if available
        file_metadata: File metadata (size, type, name)
        processing_options: Processing options (OCR, mode)
        request_id: Request correlation ID
        user_agent: User agent string
        exception: Exception object if available
        **kwargs: Additional context fields

    Returns:
        Generated request_id for correlation
    """
    # Generate request ID if not provided
    if not request_id:
        request_id = str(uuid.uuid4())

    # Build structured log context
    log_context = {
        "error_code": error_code,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Add document metadata if available
    if document_id:
        log_context["document_id"] = document_id

    # Add file metadata
    if file_metadata:
        log_context["file_size"] = file_metadata.get("size")
        log_context["file_type"] = file_metadata.get("type")
        log_context["file_name"] = file_metadata.get("name")

    # Add processing options
    if processing_options:
        log_context["processing_options"] = processing_options

    # Add user agent
    if user_agent:
        log_context["user_agent"] = user_agent

    # Add stack trace if exception is provided
    if exception:
        log_context["exception_type"] = type(exception).__name__
        log_context["stack_trace"] = traceback.format_exc()

    # Add any additional context
    log_context.update(kwargs)

    # Log error with structured context
    logger.error(
        f"Document processing failed: {error_message}",
        extra=log_context,
    )

    return request_id


def log_warning(
    warning_message: str,
    document_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log warning with context.

    Args:
        warning_message: Warning message
        document_id: Document ID if available
        **kwargs: Additional context fields
    """
    log_context = {
        "timestamp": datetime.utcnow().isoformat(),
    }

    if document_id:
        log_context["document_id"] = document_id

    log_context.update(kwargs)

    logger.warning(warning_message, extra=log_context)


def log_info(
    info_message: str,
    document_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log informational message with context.

    Args:
        info_message: Info message
        document_id: Document ID if available
        **kwargs: Additional context fields
    """
    log_context = {
        "timestamp": datetime.utcnow().isoformat(),
    }

    if document_id:
        log_context["document_id"] = document_id

    log_context.update(kwargs)

    logger.info(info_message, extra=log_context)
