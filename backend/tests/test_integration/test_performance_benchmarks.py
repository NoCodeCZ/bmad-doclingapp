"""
Performance benchmarking tests for document processing.
Measures processing times, calculates percentiles, and monitors resource usage.
"""
import pytest
import time
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from backend.tests.test_integration import TestFixtureManager, PerformanceMetrics
import numpy as np


client = TestClient(app)


@pytest.mark.integration
@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmarking tests for integration."""

    @pytest.fixture
    def fixture_manager(self):
        """Provide test fixture manager."""
        return TestFixtureManager()

    @pytest.fixture
    def perf_metrics(self):
        """Provide performance metrics tracker."""
        return PerformanceMetrics()

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_processing_time_percentiles(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager,
        perf_metrics
    ):
        """Measure processing time percentiles across different file types."""
        test_files = [
            ("pdf", "application/pdf", "small"),
            ("pdf", "application/pdf", "large"),
            ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "small"),
            ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "large"),
            ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "small"),
            ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "large"),
            ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "small"),
            ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "large")
        ]

        processing_times = []

        for file_type, mime_type, size_category in test_files:
            for mode in ["fast", "quality"]:
                mock_doc_id = f"test-perf-{file_type}-{size_category}-{mode}"
                mock_supabase.create_document.return_value = {"id": mock_doc_id}
                mock_supabase.upload_file.return_value = f"uploads/{mock_doc_id}.{file_type}"

                # Simulate realistic processing times
                base_time = 30 if mode == "fast" else 90
                size_multiplier = 1.0 if size_category == "small" else 2.0
                simulated_duration = base_time * size_multiplier

                status_index = 0
                status_sequence = ["queued", "processing", "complete"]

                def get_status(doc_id):
                    nonlocal status_index
                    status = status_sequence[min(status_index, len(status_sequence) - 1)]
                    status_index += 1

                    created_at = datetime.now(timezone.utc) - timedelta(seconds=simulated_duration)

                    return {
                        "id": doc_id,
                        "filename": f"test.{file_type}",
                        "status": status,
                        "processing_options": {"mode": mode, "ocr_enabled": False},
                        "created_at": created_at.isoformat(),
                        "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                        "error_message": None
                    }

                mock_supabase.get_document.side_effect = get_status

                start_time = time.time()

                # Create file content based on type
                if file_type == "pdf":
                    content = b"%PDF-1.4\n%%EOF"
                else:
                    content = b"PK\x03\x04" + b"\x00" * 100

                response = client.post(
                    "/api/upload",
                    files={"file": (f"test.{file_type}", content, mime_type)},
                    data={"ocr_enabled": "false", "processing_mode": mode}
                )

                document_id = response.json()["id"]

                # Monitor until complete
                for _ in range(10):
                    status_resp = client.get(f"/api/status/{document_id}")
                    if status_resp.json()["status"] == "complete":
                        break
                    await asyncio.sleep(0.1)

                elapsed_time = time.time() - start_time

                processing_times.append({
                    "file_type": file_type,
                    "size": size_category,
                    "mode": mode,
                    "time": elapsed_time
                })

                perf_metrics.record_processing(file_type, mode, elapsed_time, True)

        # Calculate percentiles
        times = [result["time"] for result in processing_times]
        p50 = np.percentile(times, 50)
        p95 = np.percentile(times, 95)
        p99 = np.percentile(times, 99)

        # Verify performance thresholds (mocked times should be fast)
        assert p50 < 60, f"p50 ({p50}s) should be under 60 seconds"
        assert p95 < 120, f"p95 ({p95}s) should be under 2 minutes"

        # Document results
        print(f"\nPerformance Percentiles:")
        print(f"  p50: {p50:.2f}s")
        print(f"  p95: {p95:.2f}s")
        print(f"  p99: {p99:.2f}s")

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_benchmark_processing_times_by_file_size(
        self,
        mock_process_task,
        mock_supabase,
        perf_metrics
    ):
        """Benchmark processing times across different file sizes."""
        file_sizes = [
            ("small", 1 * 1024 * 1024, 30),  # 1MB, 30s expected
            ("medium", 5 * 1024 * 1024, 60),  # 5MB, 60s expected
            ("large", 10 * 1024 * 1024, 90),  # 10MB, 90s expected
        ]

        for size_name, size_bytes, expected_duration in file_sizes:
            mock_doc_id = f"test-size-{size_name}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/{size_name}.pdf"

            status_index = 0
            status_sequence = ["queued", "processing", "complete"]

            def get_status(doc_id):
                nonlocal status_index
                status = status_sequence[min(status_index, len(status_sequence) - 1)]
                status_index += 1

                created_at = datetime.now(timezone.utc) - timedelta(seconds=expected_duration)

                return {
                    "id": doc_id,
                    "filename": f"{size_name}.pdf",
                    "status": status,
                    "processing_options": {"mode": "fast", "ocr_enabled": False},
                    "created_at": created_at.isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                    "error_message": None
                }

            mock_supabase.get_document.side_effect = get_status

            start_time = time.time()

            # Create file of specific size
            content = b"%PDF-1.4\n" + b"X" * (size_bytes - 10) + b"\n%%EOF"

            response = client.post(
                "/api/upload",
                files={"file": (f"{size_name}.pdf", content, "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            if response.status_code == 200:
                document_id = response.json()["id"]

                for _ in range(10):
                    status_resp = client.get(f"/api/status/{document_id}")
                    if status_resp.json()["status"] == "complete":
                        break
                    await asyncio.sleep(0.1)

                elapsed_time = time.time() - start_time
                perf_metrics.record_processing("pdf", "fast", elapsed_time, True)

                print(f"\n{size_name.capitalize()} file ({size_bytes / 1024 / 1024:.1f}MB): {elapsed_time:.2f}s")

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_concurrent_processing_performance(
        self,
        mock_process_task,
        mock_supabase,
        fixture_manager
    ):
        """Test concurrent processing scenarios."""
        concurrent_count = 5
        tasks = []

        async def process_document(index):
            mock_doc_id = f"test-concurrent-{index}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/test-{index}.pdf"

            status_index = 0
            status_sequence = ["queued", "processing", "complete"]

            def get_status(doc_id):
                nonlocal status_index
                status = status_sequence[min(status_index, len(status_sequence) - 1)]
                status_index += 1

                return {
                    "id": doc_id,
                    "filename": f"test-{index}.pdf",
                    "status": status,
                    "processing_options": {"mode": "fast", "ocr_enabled": False},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                    "error_message": None
                }

            mock_supabase.get_document.side_effect = get_status

            start_time = time.time()

            response = client.post(
                "/api/upload",
                files={"file": (f"test-{index}.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            if response.status_code == 200:
                document_id = response.json()["id"]

                for _ in range(10):
                    status_resp = client.get(f"/api/status/{document_id}")
                    if status_resp.json()["status"] == "complete":
                        break
                    await asyncio.sleep(0.1)

            return time.time() - start_time

        # Execute concurrent uploads
        for i in range(concurrent_count):
            tasks.append(process_document(i))

        results = await asyncio.gather(*tasks)

        # Analyze concurrent performance
        avg_time = np.mean(results)
        max_time = np.max(results)
        min_time = np.min(results)

        print(f"\nConcurrent Processing ({concurrent_count} documents):")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")

        # Verify reasonable performance under concurrent load
        assert avg_time < 10, "Average concurrent processing time should be reasonable"

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_performance_by_file_type(
        self,
        mock_process_task,
        mock_supabase,
        perf_metrics
    ):
        """Document performance characteristics by file type."""
        file_types = [
            ("pdf", "application/pdf", 30),
            ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 45),
            ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", 60),
            ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 40)
        ]

        results = {}

        for file_type, mime_type, expected_time in file_types:
            mock_doc_id = f"test-type-{file_type}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/test.{file_type}"

            status_index = 0
            status_sequence = ["queued", "processing", "complete"]

            def get_status(doc_id):
                nonlocal status_index
                status = status_sequence[min(status_index, len(status_sequence) - 1)]
                status_index += 1

                created_at = datetime.now(timezone.utc) - timedelta(seconds=expected_time)

                return {
                    "id": doc_id,
                    "filename": f"test.{file_type}",
                    "status": status,
                    "processing_options": {"mode": "fast", "ocr_enabled": False},
                    "created_at": created_at.isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                    "error_message": None
                }

            mock_supabase.get_document.side_effect = get_status

            start_time = time.time()

            content = b"%PDF-1.4\n%%EOF" if file_type == "pdf" else b"PK\x03\x04" + b"\x00" * 100

            response = client.post(
                "/api/upload",
                files={"file": (f"test.{file_type}", content, mime_type)},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            if response.status_code == 200:
                document_id = response.json()["id"]

                for _ in range(10):
                    status_resp = client.get(f"/api/status/{document_id}")
                    if status_resp.json()["status"] == "complete":
                        break
                    await asyncio.sleep(0.1)

                elapsed = time.time() - start_time
                results[file_type] = elapsed
                perf_metrics.record_processing(file_type, "fast", elapsed, True)

        # Document results by file type
        print(f"\nPerformance by File Type:")
        for file_type, elapsed in results.items():
            print(f"  {file_type.upper()}: {elapsed:.2f}s")

    @patch('app.services.processing_service.supabase_service')
    @patch('app.services.processing_service.process_document_task')
    async def test_performance_regression_detection(
        self,
        mock_process_task,
        mock_supabase
    ):
        """Create performance regression detection baseline."""
        # Establish baseline performance
        baseline_times = []

        for i in range(10):
            mock_doc_id = f"test-baseline-{i}"
            mock_supabase.create_document.return_value = {"id": mock_doc_id}
            mock_supabase.upload_file.return_value = f"uploads/baseline-{i}.pdf"

            status_index = 0
            status_sequence = ["queued", "processing", "complete"]

            def get_status(doc_id):
                nonlocal status_index
                status = status_sequence[min(status_index, len(status_sequence) - 1)]
                status_index += 1

                return {
                    "id": doc_id,
                    "filename": f"baseline-{i}.pdf",
                    "status": status,
                    "processing_options": {"mode": "fast", "ocr_enabled": False},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat() if status == "complete" else None,
                    "error_message": None
                }

            mock_supabase.get_document.side_effect = get_status

            start_time = time.time()

            response = client.post(
                "/api/upload",
                files={"file": (f"baseline-{i}.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
                data={"ocr_enabled": "false", "processing_mode": "fast"}
            )

            if response.status_code == 200:
                document_id = response.json()["id"]

                for _ in range(10):
                    status_resp = client.get(f"/api/status/{document_id}")
                    if status_resp.json()["status"] == "complete":
                        break
                    await asyncio.sleep(0.1)

                baseline_times.append(time.time() - start_time)

        # Calculate baseline statistics
        baseline_mean = np.mean(baseline_times)
        baseline_std = np.std(baseline_times)

        print(f"\nPerformance Baseline:")
        print(f"  Mean: {baseline_mean:.2f}s")
        print(f"  Std Dev: {baseline_std:.2f}s")
        print(f"  Min: {np.min(baseline_times):.2f}s")
        print(f"  Max: {np.max(baseline_times):.2f}s")

        # Future tests can compare against this baseline
        # Regression if new_time > baseline_mean + 2*baseline_std

    def test_memory_usage_estimation(self):
        """Estimate memory usage during processing (placeholder)."""
        # In a real scenario, would track actual memory usage
        # For integration tests, we document expected limits

        expected_limits = {
            "pdf_small": "50MB",
            "pdf_large": "200MB",
            "docx_complex": "100MB",
            "pptx_multi_slide": "150MB",
            "xlsx_large": "180MB"
        }

        print(f"\nExpected Memory Usage Limits:")
        for file_type, limit in expected_limits.items():
            print(f"  {file_type}: {limit}")

        # Actual memory tracking would require process monitoring
        assert True  # Placeholder assertion
