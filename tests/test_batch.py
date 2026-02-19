"""Tests for variant_explorer.batch."""

from pathlib import Path

import pytest

from variant_explorer.scanner import VariantScanner
from variant_explorer.batch import BatchChecker, BatchReport


@pytest.fixture()
def bim_tree(tmp_path: Path) -> Path:
    array = tmp_path / "TestArray"
    array.mkdir()
    (array / "data.bim").write_text(
        "19\trs429358\t0\t44908684\tT\tC\n"
        "19\trs7412\t0\t44908822\tC\tT\n"
    )
    return tmp_path


class TestBatchChecker:
    def test_run(self, bim_tree: Path) -> None:
        scanner = VariantScanner(bim_tree)
        checker = BatchChecker(scanner)
        report = checker.run(["rs429358", "rs7412", "rs000000"])
        assert report.total_variants == 3
        assert report.available_variants == 2
        assert report.unavailable_variants == 1
        assert report.availability_rate == pytest.approx(2 / 3)

    def test_run_from_csv(self, bim_tree: Path, tmp_path: Path) -> None:
        csv_path = tmp_path / "batch.csv"
        csv_path.write_text("variant\nrs429358\nrs000000\n")
        scanner = VariantScanner(bim_tree)
        checker = BatchChecker(scanner)
        report = checker.run_from_csv(csv_path)
        assert report.total_variants == 2
        assert report.available_variants == 1

    def test_format_report(self) -> None:
        report = BatchReport(
            total_variants=10,
            available_variants=7,
            unavailable_variants=3,
            per_array_counts={"CoreExome": 5, "GSA": 7},
        )
        text = BatchChecker.format_report(report)
        assert "70.0%" in text
        assert "CoreExome: 5" in text
