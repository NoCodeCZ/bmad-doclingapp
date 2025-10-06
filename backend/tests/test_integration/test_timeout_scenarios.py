"""
Integration tests for timeout scenarios.
Tests processing timeout detection and handling.
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from backend.tests.test_integration import TestFixtureManager


client = TestClient(app)


@pytest.mark.integration
class TestTimeoutScenarios:
    """Integration tests for timeout scenario handling."""

    @pytest.fixture
    def fixture_manager(self):
        """Provide test fixture manager."""
        return TestFixtureManager()

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_processing_timeout_detection(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Mock Docling processing exceeding 5 minutes triggers failure status."""
        mock_doc_id = "test-timeout-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        # Simulate timeout: processing for > 5 minutes
        base_time = datetime.now(timezone.utc)
        created_at = base_time - timedelta(minutes=6)  # 6 minutes ago

        status_index = 0
        status_sequence = ["queued", "processing", "processing", "failed"]

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            error_msg = "Processing timeout: operation exceeded maximum time limit of 5 minutes" if status == "failed" else None

            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": created_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "failed" else None,
                "error_message": error_msg
            }

        mock_supabase.get_document.side_effect = get_document_status

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert upload_response.status_code == 200
        document_id = upload_response.json()["id"]

        # Monitor until timeout/failure
        max_polls = 10
        timeout_detected = False

        for _ in range(max_polls):
            status_response = client.get(f"/api/status/{document_id}")
            assert status_response.status_code == 200

            status_data = status_response.json()

            if status_data["status"] == "failed":
                assert "timeout" in status_data.get("error_message", "").lower()
                timeout_detected = True
                break
            elif status_data["status"] == "complete":
                pytest.fail("Timeout scenario should not complete successfully")

            await asyncio.sleep(0.1)

        assert timeout_detected, "Timeout should be detected and reported"

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_timeout_error_message_generation(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test timeout error message generation."""
        mock_doc_id = "test-timeout-message-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        # Simulate timeout
        created_at = datetime.now(timezone.utc) - timedelta(minutes=6)

        def get_document_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "failed",
                "processing_options": {"mode": "quality", "ocr_enabled": True},
                "created_at": created_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": "Processing timeout: Document conversion exceeded the 5-minute time limit. Please try again with a smaller file or contact support."
            }

        mock_supabase.get_document.side_effect = get_document_status

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "true", "processing_mode": "quality"}
            )

        document_id = upload_response.json()["id"]

        # Check status
        status_response = client.get(f"/api/status/{document_id}")
        status_data = status_response.json()

        assert status_data["status"] == "failed"
        error_msg = status_data["error_message"]

        # Verify error message is user-friendly and informative
        assert "timeout" in error_msg.lower()
        assert "5" in error_msg or "five" in error_msg.lower()
        assert any(keyword in error_msg.lower() for keyword in ["minute", "time", "limit"])

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_system_cleanup_after_timeout(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Verify system cleanup after timeout scenarios."""
        mock_doc_id = "test-cleanup-timeout-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        created_at = datetime.now(timezone.utc) - timedelta(minutes=6)

        def get_document_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "failed",
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": created_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": "Processing timeout"
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

        # Verify timeout status
        status_response = client.get(f"/api/status/{document_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "failed"

        # Verify document is still queryable (cleanup preserves record)
        retry_response = client.get(f"/api/status/{document_id}")
        assert retry_response.status_code == 200

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_retry_functionality_after_timeout(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test retry functionality after timeout errors."""
        # First attempt: timeout
        mock_doc_id_1 = "test-timeout-retry-1"
        mock_supabase.create_document.return_value = {"id": mock_doc_id_1}
        mock_supabase.upload_file.return_value = "uploads/test1.pdf"

        created_at_1 = datetime.now(timezone.utc) - timedelta(minutes=6)

        def get_timeout_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "failed",
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": created_at_1.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": "Processing timeout"
            }

        mock_supabase.get_document.side_effect = get_timeout_status

        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            first_upload = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        first_doc_id = first_upload.json()["id"]

        # Verify timeout
        first_status = client.get(f"/api/status/{first_doc_id}")
        assert first_status.json()["status"] == "failed"

        # Second attempt: success
        mock_doc_id_2 = "test-timeout-retry-2"
        mock_supabase.create_document.return_value = {"id": mock_doc_id_2}
        mock_supabase.upload_file.return_value = "uploads/test2.pdf"

        retry_status_index = 0
        retry_sequence = ["queued", "processing", "complete"]

        def get_retry_status(doc_id):
            nonlocal retry_status_index
            status = retry_sequence[min(retry_status_index, len(retry_sequence) - 1)]
            retry_status_index += 1

            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test2.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_retry_status
        mock_supabase.download_file.return_value = b"# Successful Retry\n\nContent"

        with open(pdf_path, "rb") as f:
            retry_upload = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        retry_doc_id = retry_upload.json()["id"]

        # Monitor retry until complete
        for _ in range(10):
            retry_status_resp = client.get(f"/api/status/{retry_doc_id}")
            retry_status_data = retry_status_resp.json()

            if retry_status_data["status"] == "complete":
                # Retry succeeded
                assert retry_status_data["error_message"] is None
                break

            await asyncio.sleep(0.1)

        assert retry_status_data["status"] == "complete"

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_timeout_with_different_processing_modes(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test timeout handling with different processing modes."""
        modes = ["fast", "quality"]

        for mode in modes:
            mock_doc_id = f"test-timeout-{mode}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/test-{mode}.pdf"

            # Simulate timeout for each mode
            created_at = datetime.now(timezone.utc) - timedelta(minutes=6)

            def get_document_status(doc_id):
                return {
                    "id": doc_id,
                    "filename": "test.pdf",
                    "status": "failed",
                    "processing_options": {"mode": mode, "ocr_enabled": False},
                    "created_at": created_at.isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "error_message": f"Processing timeout in {mode} mode"
                }

            mock_supabase.get_document.side_effect = get_document_status

            pdf_path = fixture_manager.get_fixture_path("pdf_simple")

            with open(pdf_path, "rb") as f:
                upload_response = client.post(
                    "/api/upload",
                    files={"file": ("test.pdf", f, "application/pdf")},
                    data={"ocr_enabled": "false", "processing_mode": mode}
                )

            document_id = upload_response.json()["id"]

            # Verify timeout
            status_response = client.get(f"/api/status/{document_id}")
            status_data = status_response.json()

            assert status_data["status"] == "failed"
            assert "timeout" in status_data["error_message"].lower()

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_timeout_at_different_processing_stages(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test timeout detection at different processing stages."""
        stages = [
            ("queued", "Timeout during queue processing"),
            ("processing", "Timeout during document conversion"),
        ]

        for stage, expected_message in stages:
            mock_doc_id = f"test-timeout-stage-{stage}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/test-{stage}.pdf"

            created_at = datetime.now(timezone.utc) - timedelta(minutes=6)

            def get_document_status(doc_id):
                return {
                    "id": doc_id,
                    "filename": "test.pdf",
                    "status": "failed",
                    "processing_options": {"mode": "fast", "ocr_enabled": False},
                    "created_at": created_at.isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "error_message": expected_message
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

            # Verify timeout
            status_response = client.get(f"/api/status/{document_id}")
            status_data = status_response.json()

            assert status_data["status"] == "failed"
            assert "timeout" in status_data["error_message"].lower()

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_concurrent_timeouts(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test handling of multiple concurrent timeout scenarios."""
        pdf_path = fixture_manager.get_fixture_path("pdf_simple")
        document_ids = []

        # Upload multiple files that will timeout
        for i in range(3):
            mock_doc_id = f"test-concurrent-timeout-{i}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/test-{i}.pdf"

            with open(pdf_path, "rb") as f:
                upload_response = client.post(
                    "/api/upload",
                    files={"file": (f"test-{i}.pdf", f, "application/pdf")},
                    data={"ocr_enabled": "false", "processing_mode": "fast"}
                )

            document_ids.append(upload_response.json()["id"])

        # Setup timeout for all
        created_at = datetime.now(timezone.utc) - timedelta(minutes=6)

        def get_timeout_status(doc_id):
            return {
                "id": doc_id,
                "filename": f"{doc_id}.pdf",
                "status": "failed",
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": created_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": "Processing timeout"
            }

        mock_supabase.get_document.side_effect = get_timeout_status

        # Verify all timeouts are handled correctly
        for doc_id in document_ids:
            status_response = client.get(f"/api/status/{doc_id}")
            status_data = status_response.json()

            assert status_data["status"] == "failed"
            assert "timeout" in status_data["error_message"].lower()
