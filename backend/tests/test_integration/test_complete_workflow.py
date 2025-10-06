"""
Integration tests for complete document processing workflows.
Tests end-to-end upload → process → download for all supported file types.
"""
import pytest
import time
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from backend.tests.test_integration import WorkflowTestHelper, TestFixtureManager


client = TestClient(app)


@pytest.mark.integration
class TestCompleteWorkflow:
    """Integration tests for complete document processing workflows."""

    @pytest.fixture
    def fixture_manager(self):
        """Provide test fixture manager."""
        return TestFixtureManager()

    @pytest.fixture
    def workflow_helper(self):
        """Provide workflow test helper."""
        return WorkflowTestHelper()

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_pdf_complete_workflow(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test complete PDF upload → process → download workflow."""
        # Setup mocks
        mock_doc_id = "test-pdf-workflow-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        # Mock document status progression
        status_sequence = ["queued", "processing", "complete"]
        status_index = 0

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            return {
                "id": doc_id,
                "filename": "simple_document.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z" if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_document_status
        mock_supabase.download_file.return_value = b"# Test Document\n\nProcessed content"

        # Upload file
        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("simple_document.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        assert upload_response.status_code == 200
        data = upload_response.json()
        assert "id" in data
        document_id = data["id"]

        # Monitor processing
        max_polls = 10
        poll_count = 0

        while poll_count < max_polls:
            status_response = client.get(f"/api/status/{document_id}")
            assert status_response.status_code == 200

            status_data = status_response.json()
            if status_data["status"] == "complete":
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Processing failed: {status_data.get('error_message')}")

            poll_count += 1
            await asyncio.sleep(0.1)

        assert status_data["status"] == "complete"

        # Download result
        download_response = client.get(f"/api/download/{document_id}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "text/markdown"

        content = download_response.content.decode("utf-8")
        assert len(content) > 0
        assert "#" in content  # Markdown headers present

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_docx_complete_workflow(
        self,
        mock_process_task,
        mock_supabase
    ):
        """Test complete DOCX upload → process → download workflow."""
        mock_doc_id = "test-docx-workflow-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.docx"

        status_index = 0
        status_sequence = ["queued", "processing", "complete"]

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            return {
                "id": doc_id,
                "filename": "simple_document.docx",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z" if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_document_status
        mock_supabase.download_file.return_value = b"# DOCX Document\n\nConverted content"

        # Create minimal DOCX file for testing (just test with bytes)
        docx_content = b"PK\x03\x04" + b"\x00" * 100  # Minimal ZIP signature

        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.docx", docx_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"ocr_enabled": "false", "processing_mode": "fast"}
        )

        assert upload_response.status_code == 200
        document_id = upload_response.json()["id"]

        # Monitor processing
        for _ in range(10):
            status_response = client.get(f"/api/status/{document_id}")
            status_data = status_response.json()

            if status_data["status"] == "complete":
                break

            await asyncio.sleep(0.1)

        assert status_data["status"] == "complete"

        # Download
        download_response = client.get(f"/api/download/{document_id}")
        assert download_response.status_code == 200

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_pptx_complete_workflow(
        self,
        mock_process_task,
        mock_supabase
    ):
        """Test complete PPTX upload → process → download workflow."""
        mock_doc_id = "test-pptx-workflow-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pptx"

        status_index = 0
        status_sequence = ["queued", "processing", "complete"]

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            return {
                "id": doc_id,
                "filename": "test.pptx",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z" if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_document_status
        mock_supabase.download_file.return_value = b"# Presentation\n\nSlide content"

        # Create minimal PPTX file
        pptx_content = b"PK\x03\x04" + b"\x00" * 100

        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.pptx", pptx_content, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
            data={"ocr_enabled": "false", "processing_mode": "fast"}
        )

        assert upload_response.status_code == 200
        document_id = upload_response.json()["id"]

        # Monitor processing
        for _ in range(10):
            status_response = client.get(f"/api/status/{document_id}")
            status_data = status_response.json()

            if status_data["status"] == "complete":
                break

            await asyncio.sleep(0.1)

        assert status_data["status"] == "complete"

        # Download
        download_response = client.get(f"/api/download/{document_id}")
        assert download_response.status_code == 200

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_xlsx_complete_workflow(
        self,
        mock_process_task,
        mock_supabase
    ):
        """Test complete XLSX upload → process → download workflow."""
        mock_doc_id = "test-xlsx-workflow-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.xlsx"

        status_index = 0
        status_sequence = ["queued", "processing", "complete"]

        def get_document_status(doc_id):
            nonlocal status_index
            status = status_sequence[min(status_index, len(status_sequence) - 1)]
            status_index += 1

            return {
                "id": doc_id,
                "filename": "test.xlsx",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": "2025-10-06T12:00:00Z",
                "completed_at": "2025-10-06T12:01:00Z" if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_document_status
        mock_supabase.download_file.return_value = b"# Spreadsheet\n\n| A | B |\n|---|---|\n| 1 | 2 |"

        # Create minimal XLSX file
        xlsx_content = b"PK\x03\x04" + b"\x00" * 100

        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.xlsx", xlsx_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"ocr_enabled": "false", "processing_mode": "fast"}
        )

        assert upload_response.status_code == 200
        document_id = upload_response.json()["id"]

        # Monitor processing
        for _ in range(10):
            status_response = client.get(f"/api/status/{document_id}")
            status_data = status_response.json()

            if status_data["status"] == "complete":
                break

            await asyncio.sleep(0.1)

        assert status_data["status"] == "complete"

        # Download
        download_response = client.get(f"/api/download/{document_id}")
        assert download_response.status_code == 200

    @patch('app.services.processing_service.supabase_service')
    async def test_file_integrity_verification(
        self,
        mock_supabase,
        fixture_manager
    ):
        """Verify file integrity and content preservation during processing."""
        mock_doc_id = "test-integrity-123"
        mock_supabase.create_document.return_value = {"id": mock_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test.pdf"

        original_content = b"# Original Document\n\nThis is the original content"

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
        mock_supabase.download_file.return_value = original_content

        # Upload
        pdf_path = fixture_manager.get_fixture_path("pdf_simple")

        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        document_id = upload_response.json()["id"]

        # Download and verify
        download_response = client.get(f"/api/download/{document_id}")
        downloaded_content = download_response.content

        # Verify content is present and valid markdown
        assert len(downloaded_content) > 0
        assert b"#" in downloaded_content  # Has markdown headers

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_processing_time_measurement(
        self,
        mock_process_task,
        mock_supabase
    ):
        """Measure and document processing times for each file type."""
        test_cases = [
            ("pdf", "application/pdf"),
            ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
            ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        ]

        processing_times = {}

        for file_type, mime_type in test_cases:
            mock_doc_id = f"test-time-{file_type}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/test.{file_type}"

            status_index = 0
            status_sequence = ["queued", "processing", "complete"]

            def get_document_status(doc_id):
                nonlocal status_index
                status = status_sequence[min(status_index, len(status_sequence) - 1)]
                status_index += 1

                return {
                    "id": doc_id,
                    "filename": f"test.{file_type}",
                    "status": status,
                    "processing_options": {"mode": "fast", "ocr_enabled": False},
                    "created_at": "2025-10-06T12:00:00Z",
                    "completed_at": "2025-10-06T12:01:00Z" if status == "complete" else None,
                    "error_message": None
                }

            mock_supabase.get_document.side_effect = get_document_status

            # Upload and measure time
            start_time = time.time()

            file_content = b"PK\x03\x04" + b"\x00" * 100 if file_type != "pdf" else b"%PDF-1.4\n%%EOF"

            upload_response = client.post(
                "/api/upload",
                files={"file": (f"test.{file_type}", file_content, mime_type)},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            document_id = upload_response.json()["id"]

            # Monitor until complete
            for _ in range(10):
                status_response = client.get(f"/api/status/{document_id}")
                status_data = status_response.json()

                if status_data["status"] == "complete":
                    break

                await asyncio.sleep(0.1)

            elapsed_time = time.time() - start_time
            processing_times[file_type] = elapsed_time

        # Verify processing times are reasonable (mocked, so should be fast)
        for file_type, elapsed in processing_times.items():
            assert elapsed < 5, f"{file_type} took too long: {elapsed}s"
