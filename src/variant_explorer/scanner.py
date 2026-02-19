"""Core variant scanning engine.

Searches PLINK .bim files across multiple genotyping arrays to verify whether
specific genetic variants (by rsID or GRCh38 coordinate) are present.
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ScanResult:
    """Result of scanning a single variant across all arrays."""

    variant_id: str
    chromosome: Optional[str] = None
    position: Optional[int] = None
    found_in: Dict[str, bool] = field(default_factory=dict)

    @property
    def is_available(self) -> bool:
        """Return True if the variant was found in at least one array."""
        return any(self.found_in.values())

    @property
    def array_count(self) -> int:
        """Number of arrays containing this variant."""
        return sum(1 for v in self.found_in.values() if v)


class VariantScanner:
    """Scan .bim files for variant availability.

    Supports lookup by rsID (e.g. rs429358) or by GRCh38 coordinate
    (e.g. 19:44908684).

    Parameters
    ----------
    root_dir : str or Path
        Root directory containing genotyping array sub-directories with
        .bim files.
    """

    _RSID_PATTERN = re.compile(r"^rs\d+$", re.IGNORECASE)
    _COORD_PATTERN = re.compile(r"^(\d{1,2}|X|Y|MT):(\d+)$", re.IGNORECASE)

    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        if not self.root_dir.is_dir():
            raise FileNotFoundError(f"Root directory not found: {self.root_dir}")
        self._bim_index: Dict[str, List[Path]] = {}
        self._index_arrays()

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def _index_arrays(self) -> None:
        """Build an index of array-name → .bim file paths."""
        for bim_path in sorted(self.root_dir.rglob("*.bim")):
            array_name = bim_path.parent.name
            self._bim_index.setdefault(array_name, []).append(bim_path)

    @property
    def arrays(self) -> List[str]:
        """Return sorted list of discovered array names."""
        return sorted(self._bim_index.keys())

    # ------------------------------------------------------------------
    # Single-variant lookup
    # ------------------------------------------------------------------

    def _search_bim_rsid(self, bim_path: Path, rsid: str) -> bool:
        """Search a .bim file for an rsID (column 2)."""
        with open(bim_path) as fh:
            for line in fh:
                cols = line.split("\t")
                if len(cols) >= 2 and cols[1].strip() == rsid:
                    return True
        return False

    def _search_bim_coord(
        self, bim_path: Path, chrom: str, position: int
    ) -> bool:
        """Search a .bim file for a chromosome:position (columns 1 and 4)."""
        chrom_str = str(chrom)
        pos_str = str(position)
        with open(bim_path) as fh:
            for line in fh:
                cols = line.split("\t")
                if len(cols) >= 5:
                    if cols[0].strip() == chrom_str and cols[3].strip() == pos_str:
                        return True
        return False

    def check_variant(self, variant: str) -> ScanResult:
        """Check a single variant across all indexed arrays.

        Parameters
        ----------
        variant : str
            Either an rsID (e.g. ``rs429358``) or a coordinate string
            (e.g. ``19:44908684``).

        Returns
        -------
        ScanResult
        """
        coord_match = self._COORD_PATTERN.match(variant)
        if coord_match:
            chrom, pos = coord_match.group(1), int(coord_match.group(2))
            result = ScanResult(variant_id=variant, chromosome=chrom, position=pos)
            for array_name, bim_paths in self._bim_index.items():
                result.found_in[array_name] = any(
                    self._search_bim_coord(p, chrom, pos) for p in bim_paths
                )
        elif self._RSID_PATTERN.match(variant):
            result = ScanResult(variant_id=variant)
            for array_name, bim_paths in self._bim_index.items():
                result.found_in[array_name] = any(
                    self._search_bim_rsid(p, variant) for p in bim_paths
                )
        else:
            raise ValueError(
                f"Unrecognised variant format: {variant!r}. "
                "Use rsID (rs429358) or coordinate (19:44908684)."
            )
        return result

    # ------------------------------------------------------------------
    # Batch lookup
    # ------------------------------------------------------------------

    def check_variants(self, variants: List[str]) -> List[ScanResult]:
        """Check multiple variants. Returns a list of ScanResult objects."""
        return [self.check_variant(v) for v in variants]

    def check_variants_from_csv(
        self,
        csv_path: str | Path,
        variant_col: str = "variant",
    ) -> List[ScanResult]:
        """Load variants from a CSV and check each one.

        Parameters
        ----------
        csv_path : path
            CSV file with at least one column containing variant identifiers.
        variant_col : str
            Name of the column holding variant IDs.
        """
        variants: List[str] = []
        with open(csv_path, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                v = row.get(variant_col, "").strip()
                if v:
                    variants.append(v)
        return self.check_variants(variants)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def results_to_csv(
        self, results: List[ScanResult], output_path: str | Path
    ) -> None:
        """Write scan results to a CSV availability matrix."""
        arrays = self.arrays
        fieldnames = ["variant_id", "chromosome", "position"] + [
            f"found_in_{a}" for a in arrays
        ] + ["total_arrays"]

        with open(output_path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                row = {
                    "variant_id": r.variant_id,
                    "chromosome": r.chromosome or "",
                    "position": r.position or "",
                    "total_arrays": r.array_count,
                }
                for a in arrays:
                    row[f"found_in_{a}"] = "Yes" if r.found_in.get(a) else "No"
                writer.writerow(row)
