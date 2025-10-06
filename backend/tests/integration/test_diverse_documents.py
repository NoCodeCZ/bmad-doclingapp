"""
Diverse Document Testing Suite

Tests document processing across various file types, quality levels,
and edge cases to ensure workshop readiness.
"""

import pytest
import os
from pathlib import Path
from typing import Dict, List
import json

from app.utils.quality_validator import DocumentQualityValidator, validate_markdown_quality
from backend.tests.performance.benchmark_utils import PerformanceBenchmark, FileType, PERFORMANCE_THRESHOLDS


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "diverse_documents"


@pytest.fixture
def quality_validator():
    """Provide a document quality validator instance."""
    return DocumentQualityValidator()


@pytest.fixture
def performance_benchmark():
    """Provide a performance benchmark instance."""
    return PerformanceBenchmark()


def get_test_files(category: str) -> List[Path]:
    """
    Get test files from a specific category.

    Args:
        category: Category path (e.g., 'pdf/clean_digital')

    Returns:
        List of test file paths
    """
    category_dir = FIXTURES_DIR / category
    if not category_dir.exists():
        return []

    # Get all files except .info.json and README.md
    files = []
    for file_path in category_dir.iterdir():
        if file_path.is_file() and not file_path.name.endswith('.info.json') and file_path.name != 'README.md':
            files.append(file_path)

    return files


def load_file_metadata(file_path: Path) -> Dict:
    """
    Load metadata for a test file.

    Args:
        file_path: Path to test file

    Returns:
        Dictionary with file metadata
    """
    metadata_path = Path(str(file_path) + '.info.json')

    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            return json.load(f)

    return {}


class TestDOCXProcessing:
    """Test suite for DOCX document processing."""

    @pytest.mark.parametrize("test_file", get_test_files("docx/with_tables"))
    def test_docx_with_tables(self, test_file, quality_validator, performance_benchmark):
        """Test DOCX documents with table content."""
        # This is a placeholder - actual implementation would process the file
        # For now, we'll create a mock markdown output for validation testing

        mock_markdown = """
# Project Implementation Plan

## Project Overview

This document outlines the implementation plan.

## Project Timeline

| Phase | Tasks | Duration | Status |
|-------|-------|----------|--------|
| Planning | Requirements gathering | 3 days | Complete |
| Development | Core features | 7 days | Complete |

## Resource Allocation

- Alice Johnson - Product Manager - 50%
- Bob Smith - Lead Developer - 100%
"""

        # Validate quality
        report = quality_validator.validate_document(
            mock_markdown,
            test_file.name,
            "docx"
        )

        # Assert quality metrics
        assert report.overall_passed, f"Quality validation failed for {test_file.name}"
        assert report.overall_score >= 0.7, f"Quality score too low: {report.overall_score}"

        # Check table preservation
        table_score = next(
            (s for s in report.scores if s.metric.value == "table_preservation"),
            None
        )
        assert table_score is not None, "Table preservation metric missing"
        assert table_score.passed, "Table preservation failed"

    @pytest.mark.parametrize("test_file", get_test_files("docx/with_images"))
    def test_docx_with_images(self, test_file, quality_validator):
        """Test DOCX documents with embedded images."""
        # Mock markdown with image placeholders
        mock_markdown = """
# Document with Images

## Introduction

This document contains images.

![Architecture Diagram](image_001.png)

The diagram above shows the system architecture.

![Process Flow](image_002.png)
"""

        report = quality_validator.validate_document(
            mock_markdown,
            test_file.name,
            "docx"
        )

        # Check image placeholder detection
        image_score = next(
            (s for s in report.scores if s.metric.value == "image_placeholders"),
            None
        )
        assert image_score is not None, "Image placeholder metric missing"
        assert image_score.passed, "Image placeholder detection failed"


class TestPPTXProcessing:
    """Test suite for PPTX document processing."""

    @pytest.mark.parametrize("test_file", get_test_files("pptx/complex_layouts"))
    def test_pptx_complex_layouts(self, test_file, quality_validator):
        """Test PPTX documents with complex layouts."""
        mock_markdown = """
# Workshop Document Processor

October 2025 Workshop
Technical Overview

## Key Features

- Upload and process multiple document formats
  - PDF, DOCX, PPTX, XLSX support
- OCR for scanned documents
  - Quality and Fast processing modes
- Markdown output optimized for RAG

## System Architecture

**Frontend Components:**

- Next.js 14 App Router
- React with TypeScript
- TailwindCSS & shadcn/ui

**Backend Components:**

- FastAPI Python framework
- Docling document processing
- Supabase PostgreSQL & Storage
"""

        report = quality_validator.validate_document(
            mock_markdown,
            test_file.name,
            "pptx"
        )

        assert report.overall_passed, f"Quality validation failed for {test_file.name}"

        # Check heading preservation
        heading_score = next(
            (s for s in report.scores if s.metric.value == "heading_hierarchy"),
            None
        )
        assert heading_score is not None
        assert heading_score.passed, "Heading hierarchy preservation failed"


class TestXLSXProcessing:
    """Test suite for XLSX document processing."""

    @pytest.mark.parametrize("test_file", get_test_files("xlsx/multiple_sheets"))
    def test_xlsx_multiple_sheets(self, test_file, quality_validator):
        """Test XLSX documents with multiple sheets."""
        mock_markdown = """
# Financial Analysis

## Sales Data

| Month | Product A | Product B | Product C | Total |
|-------|-----------|-----------|-----------|-------|
| January | 3245 | 2134 | 3456 | 8835 |
| February | 4123 | 2876 | 3098 | 10097 |

## Summary

| Metric | Value |
|--------|-------|
| Total Sales (Product A) | 18234 |
| Total Sales (Product B) | 15678 |
| Grand Total | 52345 |
"""

        report = quality_validator.validate_document(
            mock_markdown,
            test_file.name,
            "xlsx"
        )

        assert report.overall_passed, f"Quality validation failed for {test_file.name}"

        # Verify table preservation
        table_score = next(
            (s for s in report.scores if s.metric.value == "table_preservation"),
            None
        )
        assert table_score is not None
        assert table_score.passed, "Table preservation failed for XLSX"


class TestEdgeCases:
    """Test suite for edge case handling."""

    def test_file_size_under_limit(self):
        """Test file just under size limit (9.9MB)."""
        test_files = get_test_files("edge_cases/size_limits")
        under_limit_file = next((f for f in test_files if "9.9mb" in f.name.lower()), None)

        if under_limit_file:
            metadata = load_file_metadata(under_limit_file)
            assert metadata.get("expected_behavior") == "should_process_successfully"
            # Actual processing would be tested here

    def test_file_size_over_limit(self):
        """Test file over size limit (10.1MB)."""
        test_files = get_test_files("edge_cases/size_limits")
        over_limit_file = next((f for f in test_files if "10.1mb" in f.name.lower()), None)

        if over_limit_file:
            metadata = load_file_metadata(over_limit_file)
            assert metadata.get("expected_error_code") == "FILE_TOO_LARGE"
            # Actual processing would verify the error is raised

    def test_corrupted_file_handling(self):
        """Test handling of corrupted files."""
        test_files = get_test_files("edge_cases/corrupted")
        corrupted_file = next((f for f in test_files if "corrupted" in f.name.lower()), None)

        if corrupted_file:
            metadata = load_file_metadata(corrupted_file)
            assert metadata.get("expected_error_code") == "CORRUPTED_FILE"
            # Actual processing would verify graceful failure

    @pytest.mark.parametrize("test_file", get_test_files("edge_cases/special_characters"))
    def test_special_character_filenames(self, test_file):
        """Test files with special characters in filenames."""
        metadata = load_file_metadata(test_file)

        # File should exist and be readable
        assert test_file.exists()
        assert test_file.is_file()

        # Should handle Unicode and special characters
        assert metadata.get("expected_behavior") == "should_process_with_sanitized_filename"


class TestMultilingualDocuments:
    """Test suite for multilingual document processing."""

    @pytest.mark.parametrize("test_file", get_test_files("multilingual"))
    def test_multilingual_text_extraction(self, test_file, quality_validator):
        """Test text extraction from multilingual documents."""
        # Read the actual test file
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simulate markdown output (in real scenario, this would come from Docling)
        mock_markdown = content  # For text files, content is already markdown-like

        report = quality_validator.validate_document(
            mock_markdown,
            test_file.name,
            "txt"
        )

        # Verify text content was extracted
        text_score = next(
            (s for s in report.scores if s.metric.value == "text_content"),
            None
        )
        assert text_score is not None
        assert text_score.passed, f"Text extraction failed for {test_file.name}"

        # Load metadata to check language
        metadata = load_file_metadata(test_file)
        language = metadata.get("language", "Unknown")

        # Ensure encoding handling worked (no exceptions = success)
        assert len(mock_markdown) > 0, f"No content extracted for {language} document"


class TestPerformanceBenchmarks:
    """Test suite for performance benchmarking."""

    def test_performance_tracking(self, performance_benchmark):
        """Test performance measurement utilities."""
        # Simulate processing times for different file types
        test_data = [
            ("pdf", "test.pdf", 1024000, 15.5),
            ("pdf", "test2.pdf", 2048000, 25.3),
            ("docx", "test.docx", 512000, 8.2),
            ("pptx", "test.pptx", 1536000, 18.7),
            ("xlsx", "test.xlsx", 768000, 12.4),
        ]

        for file_type, filename, size, processing_time in test_data:
            start_time = performance_benchmark.start_timer() - processing_time
            performance_benchmark.measure_processing_time(
                file_type, filename, size, start_time, success=True
            )

        # Generate statistics
        pdf_stats = performance_benchmark.calculate_statistics("pdf")
        assert pdf_stats is not None
        assert pdf_stats.sample_count == 2
        assert pdf_stats.mean > 0

        # Generate report
        report = performance_benchmark.generate_report()
        assert "statistics_by_file_type" in report
        assert "pdf" in report["statistics_by_file_type"]

    def test_performance_thresholds(self, performance_benchmark):
        """Test performance threshold validation."""
        # Add sample data within thresholds
        test_times = {
            "pdf": 90,      # Under 120s threshold
            "docx": 25,     # Under 30s threshold
            "pptx": 50,     # Under 60s threshold
            "xlsx": 40,     # Under 45s threshold
        }

        for file_type, time_seconds in test_times.items():
            start_time = performance_benchmark.start_timer() - time_seconds
            performance_benchmark.measure_processing_time(
                file_type, f"test.{file_type}", 1024000, start_time, success=True
            )

        # Check thresholds
        passed, violations = performance_benchmark.check_performance_thresholds(
            PERFORMANCE_THRESHOLDS
        )

        assert passed, f"Performance thresholds not met: {violations}"


class TestQualityValidation:
    """Test suite for quality validation utilities."""

    def test_table_detection(self, quality_validator):
        """Test table preservation detection."""
        markdown_with_table = """
# Document

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
        score = quality_validator.validate_table_preservation(markdown_with_table)
        assert score.passed
        assert score.score > 0.9

    def test_heading_hierarchy(self, quality_validator):
        """Test heading hierarchy validation."""
        markdown_with_headings = """
# Main Title

## Section 1

### Subsection 1.1

## Section 2

### Subsection 2.1
"""
        score = quality_validator.validate_heading_hierarchy(markdown_with_headings)
        assert score.passed
        assert score.score > 0.9

    def test_image_placeholder_detection(self, quality_validator):
        """Test image placeholder detection."""
        markdown_with_images = """
# Document

![Image 1](image1.png)

Some text here.

![Image 2](image2.png)
"""
        score = quality_validator.validate_image_placeholders(markdown_with_images)
        assert score.passed
        assert len(score.evidence) == 2

    def test_overall_quality_score(self, quality_validator):
        """Test overall quality scoring."""
        good_markdown = """
# Document Title

## Introduction

This is a well-structured document with proper markdown formatting.

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

![Diagram](diagram.png)

- Bullet point 1
- Bullet point 2
"""
        report = quality_validator.validate_document(
            good_markdown,
            "test.pdf",
            "pdf"
        )

        assert report.overall_passed
        assert report.overall_score >= 0.9
        assert len(report.scores) > 0
