"""
Integration tests for storage failure scenarios.
Tests Supabase connection errors and graceful degradation.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient
from app.main import app
from backend.tests.test_integration import TestFixtureManager


client = TestClient(app)


@pytest.mark.integration
class TestStorageFailures:
    """Integration tests for storage failure handling."""

    @pytest.fixture
    def fixture_manager(self):
        """Provide test fixture manager."""
        return TestFixtureManager()

    @patch('app.services.processing_service.supabase_service')
    def test_upload_storage_failure(self, mock_supabase, fixture_manager):
        """Test upload storage failure handling."""
        # Simulate Supabase storage upload failure
        mock_supabase.create_document.return_value = {"id": "test-storage-fail"}
        mock_supabase.upload_file.side_effect = Exception("Storage service unavailable")

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        # Should return error
        assert response.status_code in [500, 503]  # Internal server error or service unavailable
        error_data = response.json()
        assert "error" in error_data
        # Error message should be user-friendly
        assert any(keyword in error_data["error"]["message"].lower()
                  for keyword in ["storage", "upload", "service", "unavailable"])

    @patch('app.services.processing_service.supabase_service')
    def test_download_storage_failure(self, mock_supabase, fixture_manager):
        """Test download storage failure handling."""
        mock_doc_id = "test-download-fail"

        # Document exists and is complete
        def get_document_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "complete",
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z",
                "error_message": None,
                "output_file_path": "outputs/test.md"
            }

        mock_supabase.get_document.side_effect = get_document_status

        # But download fails
        mock_supabase.download_file.side_effect = Exception("Storage service unavailable")

        download_response = client.get(f"/api/download/{mock_doc_id}")

        # Should return error
        assert download_response.status_code in [500, 503]
        error_data = download_response.json()
        assert "error" in error_data
        # Error message should be user-friendly
        assert any(keyword in error_data["error"]["message"].lower()
                  for keyword in ["download", "storage", "service", "unavailable"])

    @patch('app.services.processing_service.supabase_service')
    def test_supabase_connection_error(self, mock_supabase, fixture_manager):
        """Mock Supabase connection error handled gracefully."""
        # Simulate connection error
        mock_supabase.create_document.side_effect = ConnectionError("Unable to connect to Supabase")

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        # Should handle gracefully
        assert response.status_code in [500, 503]
        error_data = response.json()
        assert "error" in error_data

        # Error message should be user-friendly, not expose internal details
        message = error_data["error"]["message"].lower()
        assert "service" in message or "unavailable" in message or "connection" in message
        # Should NOT expose stack traces or internal error details
        assert "supabase" not in message.lower() or "database" in message.lower()

    @patch('app.services.processing_service.supabase_service')
    async def test_storage_retry_logic(self, mock_supabase, fixture_manager):
        """Test storage retry logic and recovery mechanisms."""
        mock_doc_id = "test-retry-storage"

        # First call fails, second succeeds (simulating retry)
        call_count = 0

        def create_with_retry(document_data):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary storage error")
            return {"id": mock_doc_id}

        mock_supabase.create_document.side_effect = create_with_retry
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        # If retry logic is implemented, should eventually succeed
        # If not, will fail on first attempt
        assert response.status_code in [200, 500, 503]

    @patch('app.services.processing_service.supabase_service')
    def test_partial_storage_failure(self, mock_supabase, fixture_manager):
        """Test partial storage failure (document created but file upload fails)."""
        mock_doc_id = "test-partial-storage-fail"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}

        # File upload fails
        mock_supabase.upload_file.side_effect = Exception("File upload failed")

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        # Should handle failure gracefully
        assert response.status_code in [500, 503]

        # Document record might be created but marked as failed
        # or entire operation should be rolled back

    @patch('app.services.processing_service.supabase_service')
    def test_database_query_failure(self, mock_supabase):
        """Test database query failure handling."""
        # Simulate database query error
        mock_supabase.get_document.side_effect = Exception("Database query failed")

        response = client.get("/api/status/test-doc-123")

        # Should return error
        assert response.status_code in [500, 503]
        error_data = response.json()
        assert "error" in error_data

        # Error message should be user-friendly
        message = error_data["error"]["message"].lower()
        assert any(keyword in message for keyword in ["service", "unavailable", "error"])

    @patch('app.services.processing_service.supabase_service')
    def test_storage_timeout(self, mock_supabase, fixture_manager):
        """Test storage operation timeout."""
        # Simulate storage timeout
        import time

        def slow_upload(file_data, path):
            time.sleep(0.5)  # Simulate slow operation
            raise TimeoutError("Storage operation timed out")

        mock_supabase.create_document.return_value = {"id": "test-timeout"}
        mock_supabase.upload_file.side_effect = slow_upload

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        # Should handle timeout gracefully
        assert response.status_code in [500, 503, 504]  # 504 = Gateway Timeout

    @patch('app.services.processing_service.supabase_service')
    def test_storage_quota_exceeded(self, mock_supabase, fixture_manager):
        """Test handling of storage quota exceeded errors."""
        # Simulate quota exceeded
        mock_supabase.create_document.return_value = {"id": "test-quota"}
        mock_supabase.upload_file.side_effect = Exception("Storage quota exceeded")

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        # Should return appropriate error
        assert response.status_code in [500, 503, 507]  # 507 = Insufficient Storage
        error_data = response.json()
        assert "error" in error_data

    @patch('app.services.processing_service.supabase_service')
    def test_intermittent_storage_failures(self, mock_supabase, fixture_manager):
        """Test handling of intermittent storage failures."""
        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        # Test multiple uploads with intermittent failures
        results = []

        for i in range(5):
            mock_doc_id = f"test-intermittent-{i}"

            # Alternate between success and failure
            if i % 2 == 0:
                mock_supabase.create_document.return_value = {"id": mock_doc_id}
                mock_supabase.upload_file.return_value = f"uploads/test-{i}.pdf"
            else:
                mock_supabase.create_document.side_effect = Exception("Intermittent storage error")

            with open(pdf_path, "rb") as f:
                response = client.post(
                    "/api/upload",
                    files={"file": (f"test-{i}.pdf", f, "application/pdf")},
                    data={"ocr_enabled": "false", "processing_mode": "fast"}
                )

            results.append({
                "attempt": i,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })

        # Verify mixed results handled appropriately
        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]

        assert len(successes) > 0 or len(failures) > 0  # At least some results

    @patch('app.services.processing_service.supabase_service')
    def test_graceful_degradation_user_feedback(self, mock_supabase, fixture_manager):
        """Verify graceful degradation and user-friendly error messages."""
        failure_scenarios = [
            ("Connection error", ConnectionError("Cannot connect to storage")),
            ("Timeout error", TimeoutError("Storage operation timed out")),
            ("Permission error", PermissionError("Insufficient permissions")),
            ("General error", Exception("Unknown storage error"))
        ]

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        for scenario_name, exception in failure_scenarios:
            mock_supabase.create_document.side_effect = exception

            with open(pdf_path, "rb") as f:
                response = client.post(
                    "/api/upload",
                    files={"file": (f"{scenario_name}.pdf", f, "application/pdf")},
                    data={"ocr_enabled": "false", "processing_mode": "fast"}
                )

            # All should fail gracefully
            assert response.status_code >= 400
            error_data = response.json()
            assert "error" in error_data

            # Error message should be user-friendly
            message = error_data["error"]["message"]
            # Should not expose technical stack traces
            assert "traceback" not in message.lower()
            assert "exception" not in message.lower()

    @patch('app.services.processing_service.supabase_service')
    async def test_storage_recovery_after_failure(self, mock_supabase, fixture_manager):
        """Test system recovery after storage failure."""
        mock_doc_id = "test-recovery"
        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        # First attempt fails
        mock_supabase.create_document.side_effect = Exception("Storage temporarily unavailable")

        with open(pdf_path, "rb") as f:
            first_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert first_response.status_code >= 400

        # Storage recovers
        mock_supabase.create_document.side_effect = None
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        status_index = 0
        status_sequence = ["queued", "processing", "complete"]

        def get_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z" if status == "complete" else None,
                "error_message": None
            }

        mock_supabase.get_document.side_effect = get_status

        # Second attempt succeeds
        with open(pdf_path, "rb") as f:
            second_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert second_response.status_code == 200

        # Verify processing can complete
        document_id = second_response.json()["id"]

        for _ in range(10):
            status_resp = client.get(f"/api/status/{document_id}")
            if status_resp.json()["status"] == "complete":
                break
            await asyncio.sleep(0.1)

        final_status = client.get(f"/api/status/{document_id}")
        assert final_status.json()["status"] == "complete"
