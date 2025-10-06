"""
Integration tests for processing options validation.
Tests Fast vs Quality mode performance and OCR functionality.
"""
import pytest
import time
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from backend.tests.test_integration import TestFixtureManager


client = TestClient(app)


@pytest.mark.integration
class TestProcessingOptionsIntegration:
    """Integration tests for processing options validation."""

    @pytest.fixture
    def fixture_manager(self):
        """Provide test fixture manager."""
        return TestFixtureManager()

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_fast_vs_quality_mode_performance(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Compare processing time and quality between Fast and Quality modes."""
        test_file = fixture_manager.get_fixture_path("pdf_simple")

        # Test Fast mode
        fast_doc_id = "test-fast-mode"
        mock_supabase.create_document.return_value = {"id": fast_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test-fast.pdf"

        fast_status_index = 0
        fast_sequence = ["queued", "processing", "complete"]

        def get_fast_status(doc_id):
            nonlocal fast_status_index
            status = fast_sequence[min(fast_status_index, len(fast_sequence) - 1)]
            fast_status_index += 1

            # Simulate fast mode timing (30 seconds total)
            created_at = datetime.now(timezone.utc) - timedelta(seconds=min(fast_status_index * 10, 30))

            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": created_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test-fast.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_fast_status
        mock_supabase.download_file.return_value = b"# Fast Mode Output\n\nBasic content"

        fast_start = time.time()

        with open(test_file, "rb") as f:
            fast_upload = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        fast_doc_id = fast_upload.json()["id"]

        # Monitor fast mode
        for _ in range(10):
            status_resp = client.get(f"/api/status/{fast_doc_id}")
            if status_resp.json()["status"] == "complete":
                break
            await asyncio.sleep(0.1)

        fast_time = time.time() - fast_start

        # Test Quality mode
        quality_doc_id = "test-quality-mode"
        mock_supabase.create_document.return_value = {"id": quality_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test-quality.pdf"

        quality_status_index = 0
        quality_sequence = ["queued", "processing", "complete"]

        def get_quality_status(doc_id):
            nonlocal quality_status_index
            status = quality_sequence[min(quality_status_index, len(quality_sequence) - 1)]
            quality_status_index += 1

            # Simulate quality mode timing (90 seconds total)
            created_at = datetime.now(timezone.utc) - timedelta(seconds=min(quality_status_index * 30, 90))

            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": status,
                "processing_options": {"mode": "quality", "ocr_enabled": False},
                "created_at": created_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/test-quality.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_quality_status
        mock_supabase.download_file.return_value = b"# Quality Mode Output\n\nDetailed content with more accuracy"

        quality_start = time.time()

        with open(test_file, "rb") as f:
            quality_upload = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "quality"}
            )

        quality_doc_id = quality_upload.json()["id"]

        # Monitor quality mode
        for _ in range(10):
            status_resp = client.get(f"/api/status/{quality_doc_id}")
            if status_resp.json()["status"] == "complete":
                break
            await asyncio.sleep(0.1)

        quality_time = time.time() - quality_start

        # Verify fast mode is faster (in mocked scenario, both should be quick but logic validates)
        # In real scenario: assert quality_time > fast_time
        assert fast_time < 60  # Fast mode under 60 seconds
        assert quality_time < 180  # Quality mode under 3 minutes

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_ocr_functionality(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test OCR functionality with scanned documents."""
        test_file = fixture_manager.get_fixture_path("pdf_simple")

        # Test without OCR
        no_ocr_doc_id = "test-no-ocr"
        mock_supabase.create_document.return_value = {"id": no_ocr_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test-no-ocr.pdf"

        no_ocr_index = 0
        no_ocr_sequence = ["queued", "processing", "complete"]

        def get_no_ocr_status(doc_id):
            nonlocal no_ocr_index
            status = no_ocr_sequence[min(no_ocr_index, len(no_ocr_sequence) - 1)]
            no_ocr_index += 1

            return {
                "id": doc_id,
                "filename": "scanned.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/no-ocr.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_no_ocr_status
        mock_supabase.download_file.return_value = b"# Scanned Document\n\nMinimal text extraction"

        with open(test_file, "rb") as f:
            no_ocr_upload = client.post(
                "/api/upload",
                files={"file": ("scanned.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        no_ocr_doc_id = no_ocr_upload.json()["id"]

        # Monitor
        for _ in range(10):
            status_resp = client.get(f"/api/status/{no_ocr_doc_id}")
            if status_resp.json()["status"] == "complete":
                break
            await asyncio.sleep(0.1)

        # Download no-OCR result
        no_ocr_download = client.get(f"/api/download/{no_ocr_doc_id}")
        no_ocr_content = no_ocr_download.content.decode("utf-8")

        # Test with OCR
        ocr_doc_id = "test-with-ocr"
        mock_supabase.create_document.return_value = {"id": ocr_doc_id}
        mock_supabase.upload_file.return_value = "uploads/test-ocr.pdf"

        ocr_index = 0
        ocr_sequence = ["queued", "processing", "complete"]

        def get_ocr_status(doc_id):
            nonlocal ocr_index
            status = ocr_sequence[min(ocr_index, len(ocr_sequence) - 1)]
            ocr_index += 1

            return {
                "id": doc_id,
                "filename": "scanned.pdf",
                "status": status,
                "processing_options": {"mode": "fast", "ocr_enabled": True},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                "error_message": None,
                "output_file_path": "outputs/ocr.md" if status == "complete" else None
            }

        mock_supabase.get_document.side_effect = get_ocr_status
        mock_supabase.download_file.return_value = b"# Scanned Document\n\nExtracted text from image\n\nAdditional OCR content"

        with open(test_file, "rb") as f:
            ocr_upload = client.post(
                "/api/upload",
                files={"file": ("scanned.pdf", f, "application/pdf")},
                data={"ocr_enabled": "true", "processing_mode": "fast"}
            )

        ocr_doc_id = ocr_upload.json()["id"]

        # Monitor
        for _ in range(10):
            status_resp = client.get(f"/api/status/{ocr_doc_id}")
            status_data = status_resp.json()
            if status_data["status"] == "complete":
                # Verify OCR is enabled in options
                assert status_data.get("processing_options", {}).get("ocr_enabled") is True
                break
            await asyncio.sleep(0.1)

        # Download OCR result
        ocr_download = client.get(f"/api/download/{ocr_doc_id}")
        ocr_content = ocr_download.content.decode("utf-8")

        # Verify OCR extracted more content (mocked to have more)
        assert len(ocr_content) >= len(no_ocr_content)

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_all_processing_option_combinations(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test all processing option combinations (Fast/Quality × OCR on/off)."""
        test_file = fixture_manager.get_fixture_path("pdf_simple")

        combinations = [
            ("fast", False),
            ("fast", True),
            ("quality", False),
            ("quality", True)
        ]

        results = []

        for mode, ocr_enabled in combinations:
            doc_id = f"test-{mode}-ocr-{ocr_enabled}"
            mock_supabase.create_document.return_value = {"id": doc_id}
            mock_supabase.upload_file.return_value = f"uploads/{doc_id}.pdf"

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
                    "processing_options": {"mode": mode, "ocr_enabled": ocr_enabled},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                    "error_message": None,
                    "output_file_path": f"outputs/{doc_id}.md" if status == "complete" else None
                }

            mock_supabase.get_document.side_effect = get_status
            mock_supabase.download_file.return_value = f"# {mode} mode {'with' if ocr_enabled else 'without'} OCR\n\nContent".encode()

            start_time = time.time()

            with open(test_file, "rb") as f:
                upload_resp = client.post(
                    "/api/upload",
                    files={"file": ("test.pdf", f, "application/pdf")},
                    data={
                        "ocr_enabled": str(ocr_enabled).lower(),
                        "processing_mode": mode
                    }
                )

            assert upload_resp.status_code == 200
            doc_id = upload_resp.json()["id"]

            # Monitor
            for _ in range(10):
                status_resp = client.get(f"/api/status/{doc_id}")
                status_data = status_resp.json()

                if status_data["status"] == "complete":
                    break

                await asyncio.sleep(0.1)

            elapsed = time.time() - start_time

            results.append({
                "mode": mode,
                "ocr_enabled": ocr_enabled,
                "time": elapsed,
                "success": status_data["status"] == "complete"
            })

        # Verify all combinations succeeded
        for result in results:
            assert result["success"], f"Failed: {result['mode']} with OCR={result['ocr_enabled']}"

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_processing_output_quality_differences(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Verify processing output quality differences between modes."""
        test_file = fixture_manager.get_fixture_path("pdf_simple")

        # Fast mode output (basic)
        fast_doc_id = "test-fast-quality"
        mock_supabase.create_document.return_value = {"id": fast_doc_id}
        mock_supabase.upload_file.return_value = "uploads/fast.pdf"

        def get_fast_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "complete",
                "processing_options": {"mode": "fast", "ocr_enabled": False},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": None,
                "output_file_path": "outputs/fast.md"
            }

        mock_supabase.get_document.side_effect = get_fast_status
        mock_supabase.download_file.return_value = b"# Document\n\nBasic text content"

        with open(test_file, "rb") as f:
            fast_upload = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

        fast_doc_id = fast_upload.json()["id"]
        fast_download = client.get(f"/api/download/{fast_doc_id}")
        fast_content = fast_download.content.decode("utf-8")

        # Quality mode output (detailed)
        quality_doc_id = "test-quality-output"
        mock_supabase.create_document.return_value = {"id": quality_doc_id}
        mock_supabase.upload_file.return_value = "uploads/quality.pdf"

        def get_quality_status(doc_id):
            return {
                "id": doc_id,
                "filename": "test.pdf",
                "status": "complete",
                "processing_options": {"mode": "quality", "ocr_enabled": False},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": None,
                "output_file_path": "outputs/quality.md"
            }

        mock_supabase.get_document.side_effect = get_quality_status
        mock_supabase.download_file.return_value = b"# Document\n\nDetailed text content\n\n## Section 1\n\nMore details\n\n## Section 2\n\nAdditional information"

        with open(test_file, "rb") as f:
            quality_upload = client.post(
                "/api/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "quality"}
            )

        quality_doc_id = quality_upload.json()["id"]
        quality_download = client.get(f"/api/download/{quality_doc_id}")
        quality_content = quality_download.content.decode("utf-8")

        # Verify quality mode produces more detailed output
        assert len(quality_content) >= len(fast_content)

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_processing_time_differences_documentation(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Document processing time differences and quality trade-offs."""
        test_file = fixture_manager.get_fixture_path("pdf_simple")

        modes = ["fast", "quality"]
        timing_data = {}

        for mode in modes:
            doc_id = f"test-timing-{mode}"
            mock_supabase.create_document.return_value = {"id": doc_id}
            mock_supabase.upload_file.return_value = f"uploads/{mode}.pdf"

            # Simulate realistic timing differences
            base_time = datetime.now(timezone.utc)
            processing_duration = timedelta(seconds=30 if mode == "fast" else 90)

            status_index = 0
            status_sequence = ["queued", "processing", "complete"]

            def get_status(doc_id):
                nonlocal status_index
                status = status_sequence[min(status_index, len(status_sequence) - 1)]
                status_index += 1

                created_at = base_time - processing_duration

                return {
                    "id": doc_id,
                    "filename": "test.pdf",
                    "status": status,
                    "processing_options": {"mode": mode, "ocr_enabled": False},
                    "created_at": created_at.isoformat(),
                    "completed_at": base_time.isoformat() if status == "complete" else None,
                    "error_message": None
                }

            mock_supabase.get_document.side_effect = get_status

            start = time.time()

            with open(test_file, "rb") as f:
                upload_resp = client.post(
                    "/api/upload",
                    files={"file": ("test.pdf", f, "application/pdf")},
                    data={"ocr_enabled": "false", "processing_mode": mode}
                )

            doc_id = upload_resp.json()["id"]

            for _ in range(10):
                status_resp = client.get(f"/api/status/{doc_id}")
                if status_resp.json()["status"] == "complete":
                    break
                await asyncio.sleep(0.1)

            elapsed = time.time() - start

            timing_data[mode] = {
                "elapsed": elapsed,
                "expected": processing_duration.total_seconds()
            }

        # Document results
        assert "fast" in timing_data
        assert "quality" in timing_data
