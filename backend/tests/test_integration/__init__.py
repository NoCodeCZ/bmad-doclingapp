"""
Integration test utilities and helpers.
"""
import os
import time
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import numpy as np


class TestFixtureManager:
    """Manages test fixture files for integration testing."""

    def __init__(self, fixtures_dir: str = None):
        if fixtures_dir is None:
            fixtures_dir = os.path.join(
                os.path.dirname(__file__),
                "..",
                "fixtures",
                "integration"
            )
        self.fixtures_dir = fixtures_dir
        self.fixtures = {
            "pdf_simple": "simple_document.pdf",
            "pdf_complex": "complex_document.pdf",
            "pdf_scanned": "scanned_document.pdf",
            "docx_simple": "simple_document.docx",
            "docx_complex": "complex_document.docx",
            "pptx_simple": "simple_presentation.pptx",
            "pptx_complex": "complex_presentation.pptx",
            "xlsx_simple": "simple_spreadsheet.xlsx",
            "xlsx_complex": "complex_spreadsheet.xlsx",
            "oversized": "oversized_document.pdf",  # 11MB+
            "corrupted": "corrupted_document.pdf",
            "unsupported": "unsupported_file.txt"
        }

    def get_fixture_path(self, fixture_name: str) -> str:
        """Get absolute path to a test fixture."""
        if fixture_name not in self.fixtures:
            raise ValueError(f"Unknown fixture: {fixture_name}")
        return os.path.join(self.fixtures_dir, self.fixtures[fixture_name])

    def fixture_exists(self, fixture_name: str) -> bool:
        """Check if a fixture file exists."""
        path = self.get_fixture_path(fixture_name)
        return os.path.exists(path)

    def create_oversized_file(self, size_mb: int = 11) -> str:
        """Create an oversized file for testing."""
        filepath = self.get_fixture_path("oversized")
        size_bytes = size_mb * 1024 * 1024

        # Create a file with random content
        with open(filepath, "wb") as f:
            f.write(b"PDF-" + b"X" * (size_bytes - 4))

        return filepath

    def create_corrupted_pdf(self) -> str:
        """Create a corrupted PDF file for testing."""
        filepath = self.get_fixture_path("corrupted")

        # Create an invalid PDF file
        with open(filepath, "wb") as f:
            f.write(b"%PDF-1.4\n")
            f.write(b"corrupted data that's not valid PDF")
            f.write(b"%%EOF\n")

        return filepath

    def create_unsupported_file(self) -> str:
        """Create an unsupported file format for testing."""
        filepath = self.get_fixture_path("unsupported")

        with open(filepath, "w") as f:
            f.write("This is a plain text file that should not be supported.")

        return filepath


class PerformanceMetrics:
    """Calculate and track performance metrics for integration tests."""

    def __init__(self):
        self.processing_times: List[float] = []
        self.file_types: List[str] = []
        self.modes: List[str] = []
        self.success_count: int = 0
        self.failure_count: int = 0

    def record_processing(
        self,
        file_type: str,
        mode: str,
        time_taken: float,
        success: bool
    ):
        """Record processing time and result."""
        self.processing_times.append(time_taken)
        self.file_types.append(file_type)
        self.modes.append(mode)

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def calculate_percentiles(self) -> Dict[str, float]:
        """Calculate processing time percentiles."""
        if not self.processing_times:
            return {"p50": 0, "p95": 0, "p99": 0}

        times = np.array(self.processing_times)
        return {
            "p50": float(np.percentile(times, 50)),
            "p95": float(np.percentile(times, 95)),
            "p99": float(np.percentile(times, 99)),
        }

    def get_success_rate(self) -> float:
        """Calculate overall success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def get_metrics_by_file_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by file type."""
        metrics = {}

        for file_type in set(self.file_types):
            indices = [i for i, ft in enumerate(self.file_types) if ft == file_type]
            times = [self.processing_times[i] for i in indices]

            if times:
                metrics[file_type] = {
                    "count": len(times),
                    "avg_time": np.mean(times),
                    "min_time": np.min(times),
                    "max_time": np.max(times),
                    "p50": np.percentile(times, 50),
                    "p95": np.percentile(times, 95),
                }

        return metrics

    def get_metrics_by_mode(self) -> Dict[str, Dict]:
        """Get metrics grouped by processing mode."""
        metrics = {}

        for mode in set(self.modes):
            indices = [i for i, m in enumerate(self.modes) if m == mode]
            times = [self.processing_times[i] for i in indices]

            if times:
                metrics[mode] = {
                    "count": len(times),
                    "avg_time": np.mean(times),
                    "min_time": np.min(times),
                    "max_time": np.max(times),
                    "p50": np.percentile(times, 50),
                    "p95": np.percentile(times, 95),
                }

        return metrics


class WorkflowTestHelper:
    """Helper class for testing complete workflows."""

    @staticmethod
    async def measure_processing_time(
        client,
        file_path: str,
        processing_mode: str = "fast",
        ocr_enabled: bool = False
    ) -> Tuple[float, bool, Optional[str]]:
        """
        Measure processing time for a document.

        Returns:
            Tuple of (time_taken, success, error_message)
        """
        start_time = time.time()

        try:
            # Upload file
            with open(file_path, "rb") as f:
                filename = os.path.basename(file_path)
                mime_type = WorkflowTestHelper._get_mime_type(filename)

                upload_response = client.post(
                    "/api/upload",
                    files={"file": (filename, f, mime_type)},
                    data={
                        "ocr_enabled": str(ocr_enabled).lower(),
                        "processing_mode": processing_mode
                    }
                )

            if upload_response.status_code != 200:
                return time.time() - start_time, False, upload_response.json().get("error", {}).get("message")

            document_id = upload_response.json()["id"]

            # Poll for completion
            max_wait_time = 300  # 5 minutes
            poll_start = time.time()

            while time.time() - poll_start < max_wait_time:
                status_response = client.get(f"/api/status/{document_id}")

                if status_response.status_code != 200:
                    return time.time() - start_time, False, "Status check failed"

                status = status_response.json()

                if status["status"] == "complete":
                    return time.time() - start_time, True, None
                elif status["status"] == "failed":
                    return time.time() - start_time, False, status.get("error_message")

                await asyncio.sleep(2)

            return time.time() - start_time, False, "Processing timeout"

        except Exception as e:
            return time.time() - start_time, False, str(e)

    @staticmethod
    def _get_mime_type(filename: str) -> str:
        """Get MIME type from filename extension."""
        ext = filename.lower().split(".")[-1]
        mime_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "txt": "text/plain"
        }
        return mime_types.get(ext, "application/octet-stream")

    @staticmethod
    async def test_complete_workflow(
        client,
        file_path: str,
        processing_mode: str = "fast",
        ocr_enabled: bool = False
    ) -> Dict:
        """
        Test complete upload -> process -> download workflow.

        Returns:
            Dictionary with test results
        """
        result = {
            "success": False,
            "upload_success": False,
            "processing_success": False,
            "download_success": False,
            "error_message": None,
            "processing_time": 0,
            "document_id": None
        }

        try:
            # 1. Upload
            with open(file_path, "rb") as f:
                filename = os.path.basename(file_path)
                mime_type = WorkflowTestHelper._get_mime_type(filename)

                upload_response = client.post(
                    "/api/upload",
                    files={"file": (filename, f, mime_type)},
                    data={
                        "ocr_enabled": str(ocr_enabled).lower(),
                        "processing_mode": processing_mode
                    }
                )

            if upload_response.status_code != 200:
                result["error_message"] = upload_response.json().get("error", {}).get("message")
                return result

            result["upload_success"] = True
            result["document_id"] = upload_response.json()["id"]

            # 2. Monitor processing
            start_time = time.time()
            max_wait_time = 300

            while time.time() - start_time < max_wait_time:
                status_response = client.get(f"/api/status/{result['document_id']}")

                if status_response.status_code != 200:
                    result["error_message"] = "Status check failed"
                    return result

                status = status_response.json()

                if status["status"] == "complete":
                    result["processing_success"] = True
                    result["processing_time"] = time.time() - start_time
                    break
                elif status["status"] == "failed":
                    result["error_message"] = status.get("error_message")
                    return result

                await asyncio.sleep(2)

            if not result["processing_success"]:
                result["error_message"] = "Processing timeout"
                return result

            # 3. Download
            download_response = client.get(f"/api/download/{result['document_id']}")

            if download_response.status_code != 200:
                result["error_message"] = "Download failed"
                return result

            result["download_success"] = True
            result["success"] = True

            return result

        except Exception as e:
            result["error_message"] = str(e)
            return result
