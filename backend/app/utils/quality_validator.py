"""
Document Quality Validation Utilities

This module provides utilities for validating the quality of document
processing output, specifically for Docling markdown output validation.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class QualityMetric(Enum):
    """Quality metric types for document validation."""
    TABLE_PRESERVATION = "table_preservation"
    HEADING_HIERARCHY = "heading_hierarchy"
    IMAGE_PLACEHOLDERS = "image_placeholders"
    TEXT_CONTENT = "text_content"
    LIST_STRUCTURE = "list_structure"
    OVERALL_QUALITY = "overall_quality"


@dataclass
class QualityScore:
    """Quality score for a specific metric."""
    metric: QualityMetric
    score: float  # 0.0 to 1.0
    passed: bool
    details: str
    evidence: List[str] = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []


@dataclass
class DocumentQualityReport:
    """Complete quality report for a processed document."""
    filename: str
    file_type: str
    scores: List[QualityScore]
    overall_score: float
    overall_passed: bool
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> Dict:
        """Convert report to dictionary format."""
        return {
            "filename": self.filename,
            "file_type": self.file_type,
            "scores": [
                {
                    "metric": score.metric.value,
                    "score": score.score,
                    "passed": score.passed,
                    "details": score.details,
                    "evidence": score.evidence
                }
                for score in self.scores
            ],
            "overall_score": self.overall_score,
            "overall_passed": self.overall_passed,
            "recommendations": self.recommendations
        }


class DocumentQualityValidator:
    """Validates the quality of Docling markdown output."""

    # Quality thresholds
    PASS_THRESHOLD = 0.70  # 70% minimum to pass
    EXCELLENT_THRESHOLD = 0.90  # 90% for excellent quality

    def __init__(self):
        self.validation_results: List[QualityScore] = []

    def validate_table_preservation(self, markdown_content: str) -> QualityScore:
        """
        Validate that tables are preserved in markdown format.

        Args:
            markdown_content: The markdown output from Docling

        Returns:
            QualityScore for table preservation
        """
        # Pattern for markdown tables
        table_pattern = r'\|.*\|.*\|'
        table_header_pattern = r'\|[-:\s]+\|'

        tables_found = re.findall(table_pattern, markdown_content)
        table_headers = re.findall(table_header_pattern, markdown_content)

        # Count distinct tables (tables with headers)
        table_count = len(table_headers)

        # Extract evidence
        evidence = []
        if table_count > 0:
            # Get first few table rows as evidence
            for i, table_row in enumerate(tables_found[:3]):
                evidence.append(table_row.strip())

        # Score based on table detection
        if table_count > 0:
            score = 1.0
            passed = True
            details = f"Found {table_count} table(s) with proper markdown formatting"
        elif len(tables_found) > 0:
            score = 0.5
            passed = False
            details = "Found table-like content but missing proper headers"
        else:
            # Check if there should be tables in the content
            if "table" in markdown_content.lower():
                score = 0.0
                passed = False
                details = "Document references tables but none found in markdown"
            else:
                score = 1.0
                passed = True
                details = "No tables expected or found"

        return QualityScore(
            metric=QualityMetric.TABLE_PRESERVATION,
            score=score,
            passed=passed,
            details=details,
            evidence=evidence
        )

    def validate_heading_hierarchy(self, markdown_content: str) -> QualityScore:
        """
        Validate that heading hierarchy is properly maintained.

        Args:
            markdown_content: The markdown output from Docling

        Returns:
            QualityScore for heading hierarchy
        """
        # Pattern for markdown headings
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        headings = re.findall(heading_pattern, markdown_content, re.MULTILINE)

        if not headings:
            # No headings found
            score = 0.0
            passed = False
            details = "No headings found in markdown output"
            evidence = []
        else:
            # Analyze heading structure
            heading_levels = [len(h[0]) for h in headings]
            evidence = [f"{h[0]} {h[1]}" for h in headings[:5]]  # First 5 headings

            # Check for proper hierarchy
            has_h1 = 1 in heading_levels
            max_level = max(heading_levels)
            min_level = min(heading_levels)

            # Calculate score based on structure
            if has_h1 and max_level <= 4:
                score = 1.0
                passed = True
                details = f"Found {len(headings)} headings with proper hierarchy (H1-H{max_level})"
            elif len(headings) > 0:
                score = 0.7
                passed = True
                details = f"Found {len(headings)} headings but hierarchy could be improved"
            else:
                score = 0.3
                passed = False
                details = "Heading structure is incomplete"

        return QualityScore(
            metric=QualityMetric.HEADING_HIERARCHY,
            score=score,
            passed=passed,
            details=details,
            evidence=evidence
        )

    def validate_image_placeholders(self, markdown_content: str) -> QualityScore:
        """
        Validate that image placeholders are properly inserted.

        Args:
            markdown_content: The markdown output from Docling

        Returns:
            QualityScore for image placeholders
        """
        # Pattern for markdown images
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        images = re.findall(image_pattern, markdown_content)

        evidence = [f"![{alt}]({src})" for alt, src in images[:3]]

        if images:
            score = 1.0
            passed = True
            details = f"Found {len(images)} image placeholder(s)"
        else:
            # Check if images are expected
            if "image" in markdown_content.lower() or "figure" in markdown_content.lower():
                score = 0.0
                passed = False
                details = "Document references images but no placeholders found"
            else:
                score = 1.0
                passed = True
                details = "No images expected or found"

        return QualityScore(
            metric=QualityMetric.IMAGE_PLACEHOLDERS,
            score=score,
            passed=passed,
            details=details,
            evidence=evidence
        )

    def validate_text_content(self, markdown_content: str) -> QualityScore:
        """
        Validate that meaningful text content was extracted.

        Args:
            markdown_content: The markdown output from Docling

        Returns:
            QualityScore for text content extraction
        """
        # Remove markdown formatting to get plain text
        plain_text = re.sub(r'[#*_`\[\]()]', '', markdown_content)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()

        word_count = len(plain_text.split())
        char_count = len(plain_text)

        # Sample text for evidence
        evidence = [plain_text[:200] + "..." if len(plain_text) > 200 else plain_text]

        # Score based on content volume
        if word_count > 50:
            score = 1.0
            passed = True
            details = f"Extracted {word_count} words, {char_count} characters"
        elif word_count > 20:
            score = 0.7
            passed = True
            details = f"Extracted {word_count} words (limited content)"
        elif word_count > 0:
            score = 0.4
            passed = False
            details = f"Very limited text extraction ({word_count} words)"
        else:
            score = 0.0
            passed = False
            details = "No text content extracted"

        return QualityScore(
            metric=QualityMetric.TEXT_CONTENT,
            score=score,
            passed=passed,
            details=details,
            evidence=evidence
        )

    def validate_list_structure(self, markdown_content: str) -> QualityScore:
        """
        Validate that list structures are properly preserved.

        Args:
            markdown_content: The markdown output from Docling

        Returns:
            QualityScore for list structure preservation
        """
        # Patterns for lists
        unordered_list_pattern = r'^\s*[-*+]\s+(.+)$'
        ordered_list_pattern = r'^\s*\d+\.\s+(.+)$'

        unordered_lists = re.findall(unordered_list_pattern, markdown_content, re.MULTILINE)
        ordered_lists = re.findall(ordered_list_pattern, markdown_content, re.MULTILINE)

        total_lists = len(unordered_lists) + len(ordered_lists)

        evidence = []
        if unordered_lists:
            evidence.extend([f"- {item}" for item in unordered_lists[:2]])
        if ordered_lists:
            evidence.extend([f"1. {item}" for item in ordered_lists[:2]])

        if total_lists > 0:
            score = 1.0
            passed = True
            details = f"Found {len(unordered_lists)} unordered and {len(ordered_lists)} ordered list items"
        else:
            score = 1.0
            passed = True
            details = "No lists expected or found"

        return QualityScore(
            metric=QualityMetric.LIST_STRUCTURE,
            score=score,
            passed=passed,
            details=details,
            evidence=evidence
        )

    def calculate_overall_quality(
        self,
        scores: List[QualityScore],
        weights: Optional[Dict[QualityMetric, float]] = None
    ) -> Tuple[float, bool]:
        """
        Calculate overall quality score from individual metrics.

        Args:
            scores: List of individual quality scores
            weights: Optional weights for each metric (default: equal weights)

        Returns:
            Tuple of (overall_score, passed)
        """
        if not scores:
            return 0.0, False

        if weights is None:
            # Equal weights for all metrics
            weights = {score.metric: 1.0 for score in scores}

        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}

        # Calculate weighted average
        weighted_sum = sum(
            score.score * normalized_weights.get(score.metric, 0)
            for score in scores
        )

        overall_score = weighted_sum
        overall_passed = overall_score >= self.PASS_THRESHOLD

        return overall_score, overall_passed

    def validate_document(
        self,
        markdown_content: str,
        filename: str,
        file_type: str
    ) -> DocumentQualityReport:
        """
        Perform complete quality validation on a processed document.

        Args:
            markdown_content: The markdown output from Docling
            filename: Original filename
            file_type: File type (pdf, docx, pptx, xlsx)

        Returns:
            DocumentQualityReport with all validation results
        """
        # Run all validations
        scores = [
            self.validate_table_preservation(markdown_content),
            self.validate_heading_hierarchy(markdown_content),
            self.validate_image_placeholders(markdown_content),
            self.validate_text_content(markdown_content),
            self.validate_list_structure(markdown_content)
        ]

        # Calculate overall quality
        overall_score, overall_passed = self.calculate_overall_quality(scores)

        # Generate recommendations
        recommendations = []
        for score in scores:
            if not score.passed:
                if score.metric == QualityMetric.TABLE_PRESERVATION:
                    recommendations.append("Consider using Quality mode for better table preservation")
                elif score.metric == QualityMetric.HEADING_HIERARCHY:
                    recommendations.append("Document structure may benefit from clearer heading hierarchy")
                elif score.metric == QualityMetric.TEXT_CONTENT:
                    recommendations.append("Enable OCR if document is scanned or image-based")

        if overall_score >= self.EXCELLENT_THRESHOLD:
            recommendations.append("Excellent quality - suitable for RAG usage")
        elif overall_score >= self.PASS_THRESHOLD:
            recommendations.append("Acceptable quality - may benefit from Quality mode processing")
        else:
            recommendations.append("Low quality output - consider re-processing with Quality mode and OCR enabled")

        return DocumentQualityReport(
            filename=filename,
            file_type=file_type,
            scores=scores,
            overall_score=overall_score,
            overall_passed=overall_passed,
            recommendations=recommendations
        )


def validate_markdown_quality(
    markdown_content: str,
    filename: str,
    file_type: str
) -> Dict:
    """
    Convenience function to validate markdown quality.

    Args:
        markdown_content: The markdown output from Docling
        filename: Original filename
        file_type: File type (pdf, docx, pptx, xlsx)

    Returns:
        Dictionary with validation results
    """
    validator = DocumentQualityValidator()
    report = validator.validate_document(markdown_content, filename, file_type)
    return report.to_dict()
