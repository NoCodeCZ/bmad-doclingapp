"""
Custom exceptions for document processing application.

Implements AC 6: Backend service errors with user-friendly messages
Implements AC 8: Error logging captures full error details
"""

from typing import Optional


class DocumentProcessingError(Exception):
    """Base exception for document processing errors."""

    def __init__(
        self,
        message: str,
        code: str = "PROCESSING_ERROR",
        details: Optional[str] = None,
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class FileValidationError(DocumentProcessingError):
    """File validation related errors.

    Implements AC 2: File validation errors show specific guidance
    Implements AC 3: Unsupported format errors include allowed formats
    """

    def __init__(
        self,
        message: str,
        code: str = "FILE_VALIDATION_ERROR",
        details: Optional[str] = None,
    ):
        super().__init__(message, code, details)


class FileTooLargeError(FileValidationError):
    """File size exceeds maximum limit.

    Implements AC 2: File validation errors show specific guidance
    """

    def __init__(self, file_size_mb: float, max_size_mb: int = 10):
        message = (
            f"File too large ({file_size_mb:.1f}MB) - maximum size is {max_size_mb}MB. "
            f"Try compressing your file or splitting into multiple files."
        )
        super().__init__(message, "FILE_TOO_LARGE")


class UnsupportedFileFormatError(FileValidationError):
    """File format is not supported.

    Implements AC 3: Unsupported format errors include allowed formats
    """

    def __init__(self, file_extension: str):
        supported_formats = "PDF, DOCX, PPTX, XLSX"
        message = (
            f"Cannot process .{file_extension} files - "
            f"supported formats: {supported_formats}."
        )
        super().__init__(message, "UNSUPPORTED_FORMAT")


class ProcessingTimeoutError(DocumentProcessingError):
    """Processing timeout errors.

    Implements AC 4: Processing timeout errors display guidance
    """

    def __init__(
        self,
        message: str = "Processing took too long - try enabling Fast mode or reducing document complexity.",
    ):
        super().__init__(message, "PROCESSING_TIMEOUT")


class CorruptedFileError(DocumentProcessingError):
    """Corrupted or password-protected file errors.

    Implements AC 5: Corrupted file errors suggest solutions
    """

    def __init__(
        self,
        message: str = "Unable to process file - ensure the document isn't password-protected or corrupted.",
    ):
        super().__init__(message, "CORRUPTED_FILE")


class ServiceError(DocumentProcessingError):
    """Backend service errors (Supabase, Docling, etc.).

    Implements AC 6: Backend service errors show user-friendly messages
    """

    def __init__(
        self,
        message: str = "Processing failed due to server error - please try again.",
        code: str = "SERVICE_ERROR",
        details: Optional[str] = None,
    ):
        super().__init__(message, code, details)


class SupabaseError(ServiceError):
    """Supabase-related errors."""

    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="Storage service error - please try again.",
            code="STORAGE_ERROR",
            details=details,
        )


class DoclingProcessingError(ServiceError):
    """Docling processing errors."""

    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="Document processing failed - please try uploading a different file.",
            code="DOCLING_ERROR",
            details=details,
        )
