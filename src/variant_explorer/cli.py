"""Command-line interface for biobank-variant-explorer."""

from __future__ import annotations

import argparse
import sys

from .scanner import VariantScanner
from .batch import BatchChecker


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="variant-explorer",
        description="High-throughput variant lookup across genotyping arrays.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- scan ---
    p_scan = sub.add_parser("scan", help="Check variants against .bim files.")
    p_scan.add_argument("--root-dir", required=True, help="Root genotyping directory.")
    p_scan.add_argument("--variants", nargs="+", help="Variant IDs to check.")
    p_scan.add_argument("--csv", help="CSV file with variant IDs.")
    p_scan.add_argument("--variant-col", default="variant", help="Column name in CSV.")
    p_scan.add_argument("--output", help="Output CSV path for results matrix.")

    # --- batch ---
    p_batch = sub.add_parser("batch", help="Run batch check with summary report.")
    p_batch.add_argument("--root-dir", required=True, help="Root genotyping directory.")
    p_batch.add_argument("--csv", required=True, help="CSV file with variant IDs.")
    p_batch.add_argument("--variant-col", default="variant", help="Column name in CSV.")
    p_batch.add_argument("--output", help="Output CSV path for results matrix.")

    args = parser.parse_args(argv)

    if args.command == "scan":
        scanner = VariantScanner(args.root_dir)
        if args.csv:
            results = scanner.check_variants_from_csv(args.csv, args.variant_col)
        elif args.variants:
            results = scanner.check_variants(args.variants)
        else:
            parser.error("Provide either --variants or --csv.")
            return
        if args.output:
            scanner.results_to_csv(results, args.output)
            print(f"Results written to {args.output}")
        else:
            for r in results:
                status = "FOUND" if r.is_available else "NOT FOUND"
                print(f"{r.variant_id}: {status} (in {r.array_count} arrays)")

    elif args.command == "batch":
        scanner = VariantScanner(args.root_dir)
        checker = BatchChecker(scanner)
        report = checker.run_from_csv(args.csv, args.variant_col)
        print(checker.format_report(report))
        if args.output:
            scanner.results_to_csv(report.results, args.output)
            print(f"\nDetailed results written to {args.output}")


if __name__ == "__main__":
    main()
