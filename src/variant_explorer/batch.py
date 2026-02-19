"""Batch variant checking with progress reporting."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .scanner import ScanResult, VariantScanner


@dataclass
class BatchReport:
    """Summary report for a batch variant check."""

    total_variants: int = 0
    available_variants: int = 0
    unavailable_variants: int = 0
    per_array_counts: Dict[str, int] = field(default_factory=dict)
    results: List[ScanResult] = field(default_factory=list)

    @property
    def availability_rate(self) -> float:
        """Fraction of queried variants found in at least one array."""
        if self.total_variants == 0:
            return 0.0
        return self.available_variants / self.total_variants


class BatchChecker:
    """Run batch variant checks and produce summary reports.

    Parameters
    ----------
    scanner : VariantScanner
        An initialised scanner instance.
    """

    def __init__(self, scanner: VariantScanner) -> None:
        self.scanner = scanner

    def run(self, variants: List[str]) -> BatchReport:
        """Check a list of variants and return a summary report."""
        results = self.scanner.check_variants(variants)
        report = BatchReport(
            total_variants=len(results),
            results=results,
        )
        for r in results:
            if r.is_available:
                report.available_variants += 1
            else:
                report.unavailable_variants += 1
            for array, found in r.found_in.items():
                if found:
                    report.per_array_counts[array] = (
                        report.per_array_counts.get(array, 0) + 1
                    )
        return report

    def run_from_csv(
        self,
        csv_path: str | Path,
        variant_col: str = "variant",
    ) -> BatchReport:
        """Load variants from CSV and run the batch check."""
        variants: List[str] = []
        with open(csv_path, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                v = row.get(variant_col, "").strip()
                if v:
                    variants.append(v)
        return self.run(variants)

    @staticmethod
    def format_report(report: BatchReport) -> str:
        """Format a human-readable summary of the batch report."""
        lines = [
            "Batch Variant Check Report",
            "=" * 40,
            f"Total variants queried:  {report.total_variants}",
            f"Available (>=1 array):   {report.available_variants}",
            f"Unavailable:             {report.unavailable_variants}",
            f"Availability rate:       {report.availability_rate:.1%}",
            "",
            "Per-array hit counts:",
        ]
        for array in sorted(report.per_array_counts.keys()):
            lines.append(f"  {array}: {report.per_array_counts[array]}")
        return "\n".join(lines)
