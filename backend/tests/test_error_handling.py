"""
Comprehensive Error Handling Tests

Tests AC 2: File validation errors show specific guidance
Tests AC 3: Unsupported format errors include allowed formats
Tests AC 4: Processing timeout errors display guidance
Tests AC 5: Corrupted file errors suggest solutions
Tests AC 6: Backend service errors show user-friendly messages
Tests AC 8: Error logging captures full error details
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions import (
    FileTooLargeError,
    UnsupportedFileFormatError,
    ProcessingTimeoutError,
    CorruptedFileError,
    DoclingProcessingError,
    SupabaseError,
)

client = TestClient(app)


class TestFileValidationErrors:
    """Test AC 2 & 3: File validation error handling"""

    def test_file_too_large_error_message(self):
        """Test that file size errors show specific guidance (AC 2)"""
        error = FileTooLargeError(file_size_mb=15.0, max_size_mb=10)

        assert "15.0MB" in error.message
        assert "10MB" in error.message
        assert "compressing" in error.message.lower()
        assert error.code == "FILE_TOO_LARGE"

    def test_unsupported_format_error_message(self):
        """Test that format errors include allowed formats (AC 3)"""
        error = UnsupportedFileFormatError(file_extension="txt")

        assert ".txt" in error.message
        assert "PDF" in error.message
        assert "DOCX" in error.message
        assert "PPTX" in error.message
        assert "XLSX" in error.message
        assert error.code == "UNSUPPORTED_FORMAT"

    def test_file_validation_error_has_code(self):
        """Test that validation errors have error codes"""
        error1 = FileTooLargeError(12.5)
        error2 = UnsupportedFileFormatError("exe")

        assert error1.code == "FILE_TOO_LARGE"
        assert error2.code == "UNSUPPORTED_FORMAT"


class TestProcessingErrors:
    """Test AC 4 & 5: Processing error handling"""

    def test_processing_timeout_error_message(self):
        """Test that timeout errors display guidance (AC 4)"""
        error = ProcessingTimeoutError()

        assert "took too long" in error.message.lower()
        assert "fast mode" in error.message.lower() or "fast" in error.message.lower()
        assert "reducing" in error.message.lower()
        assert error.code == "PROCESSING_TIMEOUT"

    def test_corrupted_file_error_message(self):
        """Test that corrupted file errors suggest solutions (AC 5)"""
        error = CorruptedFileError()

        assert "password-protected" in error.message.lower()
        assert "corrupted" in error.message.lower()
        assert error.code == "CORRUPTED_FILE"


class TestServiceErrors:
    """Test AC 6: Backend service errors"""

    def test_docling_error_user_friendly_message(self):
        """Test that Docling errors show user-friendly messages (AC 6)"""
        error = DoclingProcessingError()

        # Should NOT expose technical details in main message
        assert "docling" not in error.message.lower()
        assert "processing failed" in error.message.lower()
        assert "try uploading" in error.message.lower()
        assert error.code == "DOCLING_ERROR"

    def test_supabase_error_user_friendly_message(self):
        """Test that Supabase errors show user-friendly messages (AC 6)"""
        error = SupabaseError()

        # Should NOT expose "Supabase" in user message
        assert "supabase" not in error.message.lower()
        assert "storage" in error.message.lower() or "service" in error.message.lower()
        assert "try again" in error.message.lower()
        assert error.code == "STORAGE_ERROR"

    def test_service_error_with_details(self):
        """Test that service errors can log details separately (AC 8)"""
        technical_details = "Connection refused to database at localhost:5432"
        error = SupabaseError(details=technical_details)

        # User message should be friendly
        assert "supabase" not in error.message.lower()

        # Technical details stored separately for logging
        assert error.details == technical_details


class TestErrorResponseFormat:
    """Test error response structure consistency"""

    def test_error_has_required_fields(self):
        """Test that all errors have required fields"""
        error = FileTooLargeError(12.5)

        assert hasattr(error, "message")
        assert hasattr(error, "code")
        assert error.message is not None
        assert error.code is not None

    def test_error_codes_are_unique(self):
        """Test that different error types have different codes"""
        errors = [
            FileTooLargeError(15.0),
            UnsupportedFileFormatError("txt"),
            ProcessingTimeoutError(),
            CorruptedFileError(),
            DoclingProcessingError(),
            SupabaseError(),
        ]

        codes = [e.code for e in errors]
        assert len(codes) == len(set(codes)), "Error codes should be unique"


class TestErrorMessageQuality:
    """Test error message quality and actionability"""

    def test_all_errors_are_actionable(self):
        """Test that all errors provide actionable guidance"""
        actionable_keywords = [
            "try",
            "ensure",
            "reduce",
            "compress",
            "enable",
            "upload",
            "check",
        ]

        errors = [
            FileTooLargeError(15.0),
            UnsupportedFileFormatError("txt"),
            ProcessingTimeoutError(),
            CorruptedFileError(),
            DoclingProcessingError(),
            SupabaseError(),
        ]

        for error in errors:
            message_lower = error.message.lower()
            has_actionable_guidance = any(
                keyword in message_lower for keyword in actionable_keywords
            )
            assert (
                has_actionable_guidance
            ), f"Error message should be actionable: {error.message}"

    def test_error_messages_are_user_friendly(self):
        """Test that error messages avoid technical jargon"""
        technical_terms = [
            "exception",
            "stack trace",
            "null pointer",
            "undefined",
            "traceback",
        ]

        errors = [
            FileTooLargeError(15.0),
            UnsupportedFileFormatError("txt"),
            ProcessingTimeoutError(),
            CorruptedFileError(),
            DoclingProcessingError(),
            SupabaseError(),
        ]

        for error in errors:
            message_lower = error.message.lower()
            for term in technical_terms:
                assert (
                    term not in message_lower
                ), f"Error message should avoid technical term '{term}': {error.message}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
