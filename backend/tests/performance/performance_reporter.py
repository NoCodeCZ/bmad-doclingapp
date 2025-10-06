"""
Performance Report Generator

Generates comprehensive test reports including performance metrics,
quality validation results, and workshop recommendations.
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json

from backend.tests.performance.benchmark_utils import PerformanceBenchmark, PERFORMANCE_THRESHOLDS


class TestReportGenerator:
    """Generates comprehensive test reports for workshop readiness."""

    def __init__(self):
        self.performance_data: Dict = {}
        self.quality_results: List[Dict] = []
        self.error_logs: List[Dict] = []
        self.workshop_recommendations: List[str] = []

    def add_performance_benchmark(self, benchmark: PerformanceBenchmark):
        """Add performance benchmark data to report."""
        self.performance_data = benchmark.generate_report()

    def add_quality_result(self, quality_report: Dict):
        """Add quality validation result to report."""
        self.quality_results.append(quality_report)

    def add_error_log(
        self,
        file_type: str,
        filename: str,
        error_code: str,
        error_message: str,
        timestamp: Optional[str] = None
    ):
        """Log an error for reporting."""
        self.error_logs.append({
            "file_type": file_type,
            "filename": filename,
            "error_code": error_code,
            "error_message": error_message,
            "timestamp": timestamp or datetime.now().isoformat()
        })

    def calculate_success_rate_by_type(self) -> Dict[str, float]:
        """Calculate success rate percentage by file type."""
        if not self.performance_data or "raw_metrics" not in self.performance_data:
            return {}

        type_totals = {}
        type_successes = {}

        for metric in self.performance_data["raw_metrics"]:
            file_type = metric["file_type"]
            type_totals[file_type] = type_totals.get(file_type, 0) + 1
            if metric["success"]:
                type_successes[file_type] = type_successes.get(file_type, 0) + 1

        return {
            file_type: (type_successes.get(file_type, 0) / total * 100)
            for file_type, total in type_totals.items()
        }

    def calculate_error_breakdown(self) -> Dict[str, int]:
        """Calculate error frequency by error code."""
        error_counts = {}

        for error in self.error_logs:
            error_code = error["error_code"]
            error_counts[error_code] = error_counts.get(error_code, 0) + 1

        return error_counts

    def generate_workshop_recommendations(self) -> List[str]:
        """Generate recommendations for workshop messaging based on test results."""
        recommendations = []

        # Success rate recommendations
        success_rates = self.calculate_success_rate_by_type()
        for file_type, rate in success_rates.items():
            if rate < 80:
                recommendations.append(
                    f"⚠️ {file_type.upper()} success rate is {rate:.1f}% - "
                    f"Recommend additional testing and possibly limiting {file_type} usage"
                )
            elif rate < 95:
                recommendations.append(
                    f"✓ {file_type.upper()} success rate is {rate:.1f}% - "
                    f"Acceptable but inform users of potential issues"
                )
            else:
                recommendations.append(
                    f"✅ {file_type.upper()} success rate is {rate:.1f}% - Excellent"
                )

        # Performance recommendations
        if self.performance_data and "statistics_by_file_type" in self.performance_data:
            for file_type, stats in self.performance_data["statistics_by_file_type"].items():
                threshold = PERFORMANCE_THRESHOLDS.get(file_type, 120)
                p95 = stats.get("p95_seconds", 0)

                if p95 > threshold:
                    recommendations.append(
                        f"⚠️ {file_type.upper()} p95 processing time ({p95:.1f}s) exceeds "
                        f"threshold ({threshold}s) - Set expectations for longer wait times"
                    )
                elif p95 > threshold * 0.8:
                    recommendations.append(
                        f"✓ {file_type.upper()} p95 processing time ({p95:.1f}s) is near "
                        f"threshold - Monitor during workshop"
                    )

        # Quality recommendations
        if self.quality_results:
            avg_quality = sum(r.get("overall_score", 0) for r in self.quality_results) / len(self.quality_results)
            if avg_quality < 0.7:
                recommendations.append(
                    "⚠️ Average quality score is low - Consider using Quality mode by default"
                )
            elif avg_quality >= 0.9:
                recommendations.append(
                    "✅ Excellent average quality score - Fast mode may be sufficient for most documents"
                )

        # Error pattern recommendations
        error_breakdown = self.calculate_error_breakdown()
        if error_breakdown:
            most_common_error = max(error_breakdown.items(), key=lambda x: x[1])
            recommendations.append(
                f"📊 Most common error: {most_common_error[0]} ({most_common_error[1]} occurrences) - "
                f"Prepare troubleshooting guidance"
            )

        return recommendations

    def generate_markdown_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive markdown test report.

        Args:
            output_file: Optional file path to save markdown report

        Returns:
            Markdown formatted report string
        """
        # Generate recommendations
        self.workshop_recommendations = self.generate_workshop_recommendations()

        # Calculate statistics
        success_rates = self.calculate_success_rate_by_type()
        error_breakdown = self.calculate_error_breakdown()

        # Build markdown report
        report_lines = [
            "# Diverse Document Testing Report",
            "",
            f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Target Workshop Date:** October 17, 2025",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
        ]

        # Success rate summary
        if success_rates:
            overall_success = sum(success_rates.values()) / len(success_rates)
            report_lines.extend([
                f"**Overall Success Rate:** {overall_success:.1f}%",
                "",
                "### Success Rate by File Type",
                "",
                "| File Type | Success Rate | Status |",
                "|-----------|--------------|--------|",
            ])

            for file_type, rate in sorted(success_rates.items()):
                status = "✅" if rate >= 95 else "✓" if rate >= 80 else "⚠️"
                report_lines.append(f"| {file_type.upper()} | {rate:.1f}% | {status} |")

            report_lines.append("")

        # Performance summary
        if self.performance_data and "statistics_by_file_type" in self.performance_data:
            report_lines.extend([
                "### Processing Time Distribution",
                "",
                "| File Type | Mean | Median | P95 | Threshold | Status |",
                "|-----------|------|--------|-----|-----------|--------|",
            ])

            for file_type, stats in sorted(self.performance_data["statistics_by_file_type"].items()):
                threshold = PERFORMANCE_THRESHOLDS.get(file_type, 120)
                p95 = stats.get("p95_seconds", 0)
                status = "✅" if p95 <= threshold else "⚠️"

                report_lines.append(
                    f"| {file_type.upper()} | {stats.get('mean_seconds', 0):.1f}s | "
                    f"{stats.get('median_seconds', 0):.1f}s | {p95:.1f}s | {threshold}s | {status} |"
                )

            report_lines.append("")

        # Error analysis
        if error_breakdown:
            report_lines.extend([
                "### Error Rate Breakdown",
                "",
                "| Error Code | Occurrences | Percentage |",
                "|------------|-------------|------------|",
            ])

            total_errors = sum(error_breakdown.values())
            for error_code, count in sorted(error_breakdown.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_errors * 100) if total_errors > 0 else 0
                report_lines.append(f"| {error_code} | {count} | {percentage:.1f}% |")

            report_lines.append("")

        # Quality metrics
        if self.quality_results:
            report_lines.extend([
                "## Quality Validation Results",
                "",
                f"**Total Documents Analyzed:** {len(self.quality_results)}",
                "",
            ])

            avg_quality = sum(r.get("overall_score", 0) for r in self.quality_results) / len(self.quality_results)
            report_lines.extend([
                f"**Average Quality Score:** {avg_quality:.2f} / 1.00",
                "",
                "### Quality Score Distribution",
                "",
            ])

            # Quality bins
            excellent = len([r for r in self.quality_results if r.get("overall_score", 0) >= 0.9])
            good = len([r for r in self.quality_results if 0.7 <= r.get("overall_score", 0) < 0.9])
            poor = len([r for r in self.quality_results if r.get("overall_score", 0) < 0.7])

            report_lines.extend([
                f"- **Excellent (≥0.9):** {excellent} documents ({excellent/len(self.quality_results)*100:.1f}%)",
                f"- **Good (0.7-0.9):** {good} documents ({good/len(self.quality_results)*100:.1f}%)",
                f"- **Poor (<0.7):** {poor} documents ({poor/len(self.quality_results)*100:.1f}%)",
                "",
            ])

        # Workshop recommendations
        if self.workshop_recommendations:
            report_lines.extend([
                "## Workshop Recommendations",
                "",
            ])

            for rec in self.workshop_recommendations:
                report_lines.append(f"- {rec}")

            report_lines.append("")

        # Detailed findings
        report_lines.extend([
            "---",
            "",
            "## Detailed Test Findings",
            "",
        ])

        # Performance details
        if self.performance_data:
            report_lines.extend([
                "### Performance Benchmarks",
                "",
                "```json",
                json.dumps(self.performance_data.get("statistics_by_file_type", {}), indent=2),
                "```",
                "",
            ])

        # Error log sample
        if self.error_logs:
            report_lines.extend([
                "### Sample Error Logs (Last 10)",
                "",
                "| Timestamp | File Type | Filename | Error Code | Message |",
                "|-----------|-----------|----------|------------|---------|",
            ])

            for error in self.error_logs[-10:]:
                report_lines.append(
                    f"| {error['timestamp'][:19]} | {error['file_type']} | "
                    f"{error['filename']} | {error['error_code']} | {error['error_message'][:50]}... |"
                )

            report_lines.append("")

        # Conclusions
        report_lines.extend([
            "---",
            "",
            "## Conclusions and Next Steps",
            "",
            "### System Readiness",
            "",
        ])

        if success_rates:
            overall_success = sum(success_rates.values()) / len(success_rates)
            if overall_success >= 95:
                report_lines.append("✅ **READY FOR WORKSHOP** - System demonstrates excellent reliability")
            elif overall_success >= 85:
                report_lines.append("✓ **ACCEPTABLE FOR WORKSHOP** - Minor issues documented, workarounds available")
            else:
                report_lines.append("⚠️ **REQUIRES ATTENTION** - Success rate below target, additional testing recommended")

        report_lines.extend([
            "",
            "### Action Items",
            "",
            "1. Review error patterns and implement fixes for common failures",
            "2. Update user documentation with known limitations and workarounds",
            "3. Prepare facilitator quick-reference guide based on test findings",
            "4. Conduct final validation test with workshop-representative documents",
            "5. Set up monitoring and alerting for production deployment",
            "",
            "---",
            "",
            "*This report generated automatically from test execution results.*"
        ])

        markdown_report = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(markdown_report)

        return markdown_report

    def generate_facilitator_guide(self, output_file: Optional[str] = None) -> str:
        """
        Generate quick-reference guide for workshop facilitators.

        Args:
            output_file: Optional file path to save guide

        Returns:
            Markdown formatted guide string
        """
        success_rates = self.calculate_success_rate_by_type()
        error_breakdown = self.calculate_error_breakdown()

        guide_lines = [
            "# Workshop Facilitator Quick Reference Guide",
            "",
            f"**Workshop Date:** October 17, 2025",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "---",
            "",
            "## Quick Stats",
            "",
        ]

        if success_rates:
            guide_lines.append("### Success Rates")
            guide_lines.append("")
            for file_type, rate in sorted(success_rates.items()):
                emoji = "✅" if rate >= 95 else "✓" if rate >= 80 else "⚠️"
                guide_lines.append(f"- {emoji} **{file_type.upper()}:** {rate:.0f}% success rate")
            guide_lines.append("")

        guide_lines.extend([
            "## Common Issues & Solutions",
            "",
        ])

        if error_breakdown:
            for error_code in sorted(error_breakdown.keys(), key=lambda x: error_breakdown[x], reverse=True)[:5]:
                count = error_breakdown[error_code]
                guide_lines.extend([
                    f"### {error_code} ({count} occurrences)",
                    "",
                ])

                # Add solutions based on error code
                if error_code == "FILE_TOO_LARGE":
                    guide_lines.extend([
                        "**Solution:** Ask user to:",
                        "1. Split document into smaller sections",
                        "2. Compress PDF using Adobe Acrobat",
                        "3. Remove unnecessary images",
                        "",
                    ])
                elif error_code == "PASSWORD_PROTECTED":
                    guide_lines.extend([
                        "**Solution:** Ask user to:",
                        "1. Remove password protection before upload",
                        "2. Save as unprotected copy",
                        "",
                    ])
                elif error_code == "CORRUPTED_FILE":
                    guide_lines.extend([
                        "**Solution:**",
                        "1. Try re-saving document in original application",
                        "2. Convert to different format (e.g., PDF to DOCX)",
                        "3. Use alternative document if available",
                        "",
                    ])

        guide_lines.extend([
            "## Processing Time Expectations",
            "",
            "| File Type | Typical Time | Max Time |",
            "|-----------|--------------|----------|",
            "| PDF (digital) | 15-30s | 2 min |",
            "| PDF (scanned) | 1-2 min | 5 min |",
            "| DOCX | 10-20s | 30s |",
            "| PPTX | 20-40s | 1 min |",
            "| XLSX | 15-30s | 45s |",
            "",
            "## Best Practices to Share",
            "",
            "1. **Use digital documents** when possible (not scans)",
            "2. **Start with Fast mode** for testing, switch to Quality for final",
            "3. **Keep files under 5MB** for optimal performance",
            "4. **Enable OCR** only for scanned documents",
            "5. **Review output** before using in Open WebUI",
            "",
            "## Emergency Contacts",
            "",
            "- **Technical Issues:** [Developer contact TBD]",
            "- **System Down:** [Escalation path TBD]",
            "- **Documentation:** Check Instructions page in app",
            "",
            "---",
            "",
            "*Keep this guide handy during the workshop for quick troubleshooting.*"
        ])

        facilitator_guide = "\n".join(guide_lines)

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(facilitator_guide)

        return facilitator_guide
