"""Tests for variant_explorer.scanner."""

import csv
import textwrap
from pathlib import Path

import pytest

from variant_explorer.scanner import ScanResult, VariantScanner


@pytest.fixture()
def bim_tree(tmp_path: Path) -> Path:
    """Create a minimal directory tree with .bim files."""
    array_a = tmp_path / "ArrayA"
    array_a.mkdir()
    bim_a = array_a / "data.bim"
    bim_a.write_text(
        "19\trs429358\t0\t44908684\tT\tC\n"
        "19\trs7412\t0\t44908822\tC\tT\n"
    )
    array_b = tmp_path / "ArrayB"
    array_b.mkdir()
    bim_b = array_b / "data.bim"
    bim_b.write_text(
        "6\trs9275319\t0\t32665874\tA\tG\n"
    )
    return tmp_path


class TestVariantScanner:
    def test_arrays_discovered(self, bim_tree: Path) -> None:
        scanner = VariantScanner(bim_tree)
        assert scanner.arrays == ["ArrayA", "ArrayB"]

    def test_rsid_found(self, bim_tree: Path) -> None:
        scanner = VariantScanner(bim_tree)
        result = scanner.check_variant("rs429358")
        assert result.is_available
        assert result.found_in["ArrayA"] is True
        assert result.found_in["ArrayB"] is False

    def test_coordinate_found(self, bim_tree: Path) -> None:
        scanner = VariantScanner(bim_tree)
        result = scanner.check_variant("19:44908684")
        assert result.is_available
        assert result.array_count == 1

    def test_variant_not_found(self, bim_tree: Path) -> None:
        scanner = VariantScanner(bim_tree)
        result = scanner.check_variant("rs999999")
        assert not result.is_available
        assert result.array_count == 0

    def test_invalid_format_raises(self, bim_tree: Path) -> None:
        scanner = VariantScanner(bim_tree)
        with pytest.raises(ValueError, match="Unrecognised variant format"):
            scanner.check_variant("badformat")

    def test_check_variants_from_csv(self, bim_tree: Path, tmp_path: Path) -> None:
        csv_path = tmp_path / "query.csv"
        csv_path.write_text("variant\nrs429358\nrs9275319\nrs000000\n")
        scanner = VariantScanner(bim_tree)
        results = scanner.check_variants_from_csv(csv_path)
        assert len(results) == 3
        assert results[0].is_available
        assert results[1].is_available
        assert not results[2].is_available

    def test_results_to_csv(self, bim_tree: Path, tmp_path: Path) -> None:
        scanner = VariantScanner(bim_tree)
        results = scanner.check_variants(["rs429358", "rs9275319"])
        out = tmp_path / "output.csv"
        scanner.results_to_csv(results, out)
        with open(out) as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 2
        assert rows[0]["found_in_ArrayA"] == "Yes"


class TestScanResult:
    def test_empty_result(self) -> None:
        r = ScanResult(variant_id="rs1")
        assert not r.is_available
        assert r.array_count == 0

    def test_populated_result(self) -> None:
        r = ScanResult(variant_id="rs1", found_in={"A": True, "B": False, "C": True})
        assert r.is_available
        assert r.array_count == 2
