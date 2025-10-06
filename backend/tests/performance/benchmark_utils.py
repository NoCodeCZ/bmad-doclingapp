"""
Performance Benchmarking Utilities

This module provides utilities for measuring and analyzing document
processing performance across different file types and sizes.
"""

import time
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class FileType(Enum):
    """Supported file types for benchmarking."""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    TXT = "txt"


@dataclass
class PerformanceMetric:
    """Individual performance measurement."""
    file_type: str
    filename: str
    file_size_bytes: int
    processing_time_seconds: float
    timestamp: str
    success: bool
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class PerformanceStatistics:
    """Statistical analysis of performance metrics."""
    file_type: str
    sample_count: int
    mean: float
    median: float
    p50: float
    p95: float
    p99: float
    min: float
    max: float
    std_dev: float
    success_rate: float

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "file_type": self.file_type,
            "sample_count": self.sample_count,
            "mean_seconds": round(self.mean, 2),
            "median_seconds": round(self.median, 2),
            "p50_seconds": round(self.p50, 2),
            "p95_seconds": round(self.p95, 2),
            "p99_seconds": round(self.p99, 2),
            "min_seconds": round(self.min, 2),
            "max_seconds": round(self.max, 2),
            "std_dev": round(self.std_dev, 2),
            "success_rate_percent": round(self.success_rate * 100, 2)
        }


class PerformanceBenchmark:
    """Performance measurement and analysis tool for document processing."""

    def __init__(self):
        self.metrics: List[PerformanceMetric] = []

    def start_timer(self) -> float:
        """
        Start a performance timer.

        Returns:
            Start time in seconds
        """
        return time.time()

    def measure_processing_time(
        self,
        file_type: str,
        filename: str,
        file_size_bytes: int,
        start_time: float,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> PerformanceMetric:
        """
        Record a performance measurement.

        Args:
            file_type: Type of file being processed
            filename: Name of the file
            file_size_bytes: Size of the file in bytes
            start_time: Start time from start_timer()
            success: Whether processing succeeded
            error_message: Error message if failed
            metadata: Additional metadata

        Returns:
            PerformanceMetric object
        """
        processing_time = time.time() - start_time

        metric = PerformanceMetric(
            file_type=file_type,
            filename=filename,
            file_size_bytes=file_size_bytes,
            processing_time_seconds=processing_time,
            timestamp=datetime.now().isoformat(),
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )

        self.metrics.append(metric)
        return metric

    def get_metrics_by_type(self, file_type: str) -> List[PerformanceMetric]:
        """
        Get all metrics for a specific file type.

        Args:
            file_type: File type to filter by

        Returns:
            List of metrics for the file type
        """
        return [m for m in self.metrics if m.file_type == file_type]

    def calculate_statistics(
        self,
        file_type: str,
        include_failures: bool = False
    ) -> Optional[PerformanceStatistics]:
        """
        Calculate statistical analysis for a file type.

        Args:
            file_type: File type to analyze
            include_failures: Whether to include failed processing attempts

        Returns:
            PerformanceStatistics object or None if no data
        """
        metrics = self.get_metrics_by_type(file_type)

        if not metrics:
            return None

        # Filter for successful runs if requested
        if not include_failures:
            success_metrics = [m for m in metrics if m.success]
        else:
            success_metrics = metrics

        if not success_metrics:
            return None

        # Extract processing times
        times = [m.processing_time_seconds for m in success_metrics]

        # Calculate success rate
        success_count = len([m for m in metrics if m.success])
        success_rate = success_count / len(metrics) if metrics else 0.0

        # Calculate statistics
        stats = PerformanceStatistics(
            file_type=file_type,
            sample_count=len(success_metrics),
            mean=statistics.mean(times),
            median=statistics.median(times),
            p50=self._percentile(times, 50),
            p95=self._percentile(times, 95),
            p99=self._percentile(times, 99),
            min=min(times),
            max=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0.0,
            success_rate=success_rate
        )

        return stats

    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        Calculate percentile of data.

        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def generate_report(
        self,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        Generate a comprehensive performance report.

        Args:
            output_file: Optional file path to save JSON report

        Returns:
            Dictionary with performance report
        """
        # Get unique file types
        file_types = set(m.file_type for m in self.metrics)

        # Calculate statistics for each type
        statistics_by_type = {}
        for file_type in file_types:
            stats = self.calculate_statistics(file_type)
            if stats:
                statistics_by_type[file_type] = stats.to_dict()

        # Overall statistics
        total_measurements = len(self.metrics)
        successful_measurements = len([m for m in self.metrics if m.success])
        failed_measurements = total_measurements - successful_measurements

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_measurements": total_measurements,
                "successful_measurements": successful_measurements,
                "failed_measurements": failed_measurements,
                "overall_success_rate_percent": round(
                    (successful_measurements / total_measurements * 100) if total_measurements > 0 else 0,
                    2
                )
            },
            "statistics_by_file_type": statistics_by_type,
            "raw_metrics": [
                {
                    "file_type": m.file_type,
                    "filename": m.filename,
                    "file_size_bytes": m.file_size_bytes,
                    "processing_time_seconds": round(m.processing_time_seconds, 2),
                    "timestamp": m.timestamp,
                    "success": m.success,
                    "error_message": m.error_message,
                    "metadata": m.metadata
                }
                for m in self.metrics
            ]
        }

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

        return report

    def check_performance_thresholds(
        self,
        thresholds: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """
        Check if performance meets specified thresholds.

        Args:
            thresholds: Dictionary mapping file_type to max p95 time in seconds

        Returns:
            Tuple of (all_passed, violations)
        """
        violations = []

        for file_type, max_p95 in thresholds.items():
            stats = self.calculate_statistics(file_type)

            if stats is None:
                violations.append(f"{file_type}: No performance data available")
                continue

            if stats.p95 > max_p95:
                violations.append(
                    f"{file_type}: p95 {stats.p95:.2f}s exceeds threshold {max_p95:.2f}s"
                )

        return len(violations) == 0, violations

    def compare_processing_modes(
        self,
        file_type: str,
        mode_key: str = "processing_mode"
    ) -> Dict:
        """
        Compare performance across different processing modes.

        Args:
            file_type: File type to analyze
            mode_key: Metadata key containing mode information

        Returns:
            Dictionary with mode comparison
        """
        metrics = self.get_metrics_by_type(file_type)

        # Group by mode
        modes: Dict[str, List[float]] = {}
        for metric in metrics:
            if metric.success and mode_key in metric.metadata:
                mode = metric.metadata[mode_key]
                if mode not in modes:
                    modes[mode] = []
                modes[mode].append(metric.processing_time_seconds)

        # Calculate stats for each mode
        comparison = {}
        for mode, times in modes.items():
            if times:
                comparison[mode] = {
                    "count": len(times),
                    "mean": round(statistics.mean(times), 2),
                    "median": round(statistics.median(times), 2),
                    "p95": round(self._percentile(times, 95), 2)
                }

        return comparison

    def export_metrics_csv(self, output_file: str):
        """
        Export metrics to CSV format.

        Args:
            output_file: Path to output CSV file
        """
        import csv

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='') as f:
            fieldnames = [
                'timestamp', 'file_type', 'filename', 'file_size_bytes',
                'processing_time_seconds', 'success', 'error_message'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for metric in self.metrics:
                writer.writerow({
                    'timestamp': metric.timestamp,
                    'file_type': metric.file_type,
                    'filename': metric.filename,
                    'file_size_bytes': metric.file_size_bytes,
                    'processing_time_seconds': round(metric.processing_time_seconds, 2),
                    'success': metric.success,
                    'error_message': metric.error_message or ''
                })


# Performance threshold constants (from requirements)
PERFORMANCE_THRESHOLDS = {
    FileType.PDF.value: 120,      # 2 minutes p95
    FileType.DOCX.value: 30,      # 30 seconds p95
    FileType.PPTX.value: 60,      # 1 minute p95
    FileType.XLSX.value: 45,      # 45 seconds p95
}
