"""
Integration tests for error scenarios.
Tests oversized files, unsupported formats, and corrupted file handling.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from backend.tests.test_integration import TestFixtureManager


client = TestClient(app)


@pytest.mark.integration
@pytest.mark.error_scenario
class TestErrorScenarios:
    """Integration tests for error scenario handling."""

    @pytest.fixture
    def fixture_manager(self):
        """Provide test fixture manager."""
        return TestFixtureManager()

    def test_oversized_file_rejection(self, fixture_manager):
        """Test rejection of oversized files (11MB+)."""
        # Create 11MB file
        oversized_path = fixture_manager.get_fixture_path("oversized")

        with open(oversized_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("oversized.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert response.status_code == 400
        error_data = response.json()
        assert "error" in error_data
        assert "FILE_TOO_LARGE" in error_data["error"]["code"]
        assert "maximum size is 10MB" in error_data["error"]["message"].lower()

    def test_unsupported_format_rejection(self, fixture_manager):
        """Test rejection of unsupported file formats."""
        unsupported_path = fixture_manager.get_fixture_path("unsupported")

        with open(unsupported_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.txt", f, "text/plain")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert response.status_code == 400
        error_data = response.json()
        assert "error" in error_data
        assert "UNSUPPORTED_FORMAT" in error_data["error"]["code"]
        assert "supported formats" in error_data["error"]["message"].lower()
        assert any(fmt in error_data["error"]["message"].lower() for fmt in ["pdf", "docx", "pptx", "xlsx"])

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_corrupted_file_handling(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test handling of corrupted files."""
        corrupted_path = fixture_manager.get_fixture_path("corrupted")

        mock_doc_id = "test-corrupted-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/corrupted.pdf"

        # Corrupted file should fail during processing
        status_index = 0
        status_sequence = ["queued", "processing", "failed"]

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            error_msg = "File appears to be corrupted or invalid" if status == "failed" else None

            return {
                "id": doc_id,
                "filename": "corrupted.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z" if status == "failed" else None,
                "error_message": error_msg
            }

        mock_supabase.get_document.side_effect = get_document_status

        # Upload should succeed
        with open(corrupted_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("corrupted.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert upload_response.status_code == 200
        document_id = upload_response.json()["id"]

        # Monitor processing until failure
        max_polls = 10
        poll_count = 0
        failed = False

        while poll_count < max_polls:
            status_response = client.get(f"/api/status/{document_id}")
            assert status_response.status_code == 200

            status = status_response.json()

            if status["status"] == "failed":
                assert "corrupted" in status.get("error_message", "").lower() or "invalid" in status.get("error_message", "").lower()
                failed = True
                break
            elif status["status"] == "complete":
                pytest.fail("Corrupted file should not process successfully")

            poll_count += 1
            await asyncio.sleep(0.1)

        assert failed, "Corrupted file processing should fail"

    @patch('app.services.processing_service.supabase_service')
    def test_error_messages_are_user_friendly(self, mock_supabase):
        """Verify error messages are user-friendly and actionable."""
        test_cases = [
            {
                "filename": "oversized.pdf",
                "size": 11 * 1024 * 1024,
                "expected_code": "FILE_TOO_LARGE",
                "expected_keywords": ["maximum", "10mb", "size"]
            },
            {
                "filename": "test.txt",
                "mime": "text/plain",
                "expected_code": "UNSUPPORTED_FORMAT",
                "expected_keywords": ["supported", "format", "pdf", "docx"]
            },
            {
                "filename": "test.jpg",
                "mime": "image/jpeg",
                "expected_code": "UNSUPPORTED_FORMAT",
                "expected_keywords": ["supported", "format"]
            }
        ]

        for test_case in test_cases:
            if "size" in test_case:
                # Test oversized file
                content = b"X" * test_case["size"]
            else:
                content = b"test content"

            mime_type = test_case.get("mime", "application/pdf")

            response = client.post(
                "/api/upload",
                files={"file": (test_case["filename"], content, mime_type)},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            assert response.status_code == 400
            error_data = response.json()
            assert "error" in error_data
            assert test_case["expected_code"] in error_data["error"]["code"]

            message = error_data["error"]["message"].lower()
            for keyword in test_case["expected_keywords"]:
                assert keyword.lower() in message, f"Expected '{keyword}' in error message"

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_error_state_cleanup(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test error state cleanup and recovery."""
        mock_doc_id = "test-cleanup-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        # Simulate error during processing
        def get_document_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "failed",
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:00:30Z",
                "error_message": "Processing failed due to internal error"
            }

        mock_supabase.get_document.side_effect = get_document_status

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        document_id = upload_response.json()["id"]

        # Check status shows error
        status_response = client.get(f"/api/status/{document_id}")
        status_data = status_response.json()

        assert status_data["status"] == "failed"
        assert status_data["error_message"] is not None

        # Verify we can still query the document (not deleted/corrupted)
        retry_status = client.get(f"/api/status/{document_id}")
        assert retry_status.status_code == 200

    def test_multiple_validation_errors(self):
        """Test handling of files with multiple issues."""
        # Oversized AND unsupported format
        oversized_txt_content = b"X" * (11 * 1024 * 1024)

        response = client.post(
            "/api/upload",
            files={"file": ("oversized.txt", oversized_txt_content, "text/plain")},
            data={"ocr_enabled": "false", "processing_mode": "fast"}
        )

        assert response.status_code == 400
        error_data = response.json()

        # Should catch at least one validation error
        assert "error" in error_data
        assert error_data["error"]["code"] in ["FILE_TOO_LARGE", "UNSUPPORTED_FORMAT"]

    def test_empty_file_rejection(self):
        """Test rejection of empty files."""
        empty_content = b""

        response = client.post(
            "/api/upload",
            files={"file": ("empty.pdf", empty_content, "application/pdf")},
            data={"ocr_enabled": "false", "processing_mode": "fast"}
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "error" in error_data
        # Should indicate file is empty or invalid
        assert any(keyword in error_data["error"]["message"].lower() for keyword in ["empty", "invalid", "size"])

    @patch('app.services.processing_service.supabase_service')
    def test_invalid_processing_options(self, mock_supabase):
        """Test handling of invalid processing options."""
        mock_supabase.create_document.return_value = {"id": "test-123"}

        test_cases = [
            {"ocr_enabled": "invalid", "processing_mode": "fast"},
            {"ocr_enabled": "false", "processing_mode": "invalid_mode"},
            {"ocr_enabled": "false"},  # Missing processing_mode
        ]

        for options in test_cases:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
                data=options
            )

            # Should either validate and use defaults or reject
            if response.status_code == 400:
                error_data = response.json()
                assert "error" in error_data

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_processing_failure_with_partial_results(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test handling of processing failures with partial results."""
        mock_doc_id = "test-partial-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        status_index = 0
        status_sequence = ["queued", "processing", "failed"]

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:00:30Z" if status == "failed" else None,
                "error_message": "Processing failed after partial conversion" if status == "failed" else None,
                "output_file_path": None  # No output on failure
            }

        mock_supabase.get_document.side_effect = get_document_status

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        document_id = upload_response.json()["id"]

        # Monitor until failed
        for _ in range(10):
            status_response = client.get(f"/api/status/{document_id}")
            status_data = status_response.json()

            if status_data["status"] == "failed":
                # Verify error message is present
                assert status_data["error_message"] is not None
                # Verify no download is available
                download_response = client.get(f"/api/download/{document_id}")
                assert download_response.status_code == 404  # or 400, depending on implementation
                break

            await asyncio.sleep(0.1)

    @patch('app.services.processing_service.supabase_service')
    def test_special_characters_in_filename(self, mock_supabase):
        """Test handling of special characters in filenames."""
        mock_supabase.create_document.return_value = {"id": "test-special-123"}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        special_filenames = [
            "test file.pdf",
            "test-file.pdf",
            "test_file.pdf",
            "test.file.pdf",
            "test (1).pdf",
            "test[1].pdf",
        ]

        for filename in special_filenames:
            response = client.post(
                "/api/upload",
                files={"file": (filename, b"%PDF-1.4\n%%EOF", "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            # Should handle gracefully
            assert response.status_code in [200, 400]

            if response.status_code == 400:
                error_data = response.json()
                assert "error" in error_data
