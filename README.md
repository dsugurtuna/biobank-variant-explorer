# Biobank Variant Explorer

[![CI](https://github.com/dsugurtuna/biobank-variant-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/dsugurtuna/biobank-variant-explorer/actions)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Portfolio](https://img.shields.io/badge/Status-Portfolio_Project-purple.svg)]()

High-throughput variant discovery tool that scans PLINK `.bim` files across multiple genotyping arrays to verify whether specific genetic variants are present.

> **Portfolio disclaimer:** This repository contains sanitised, generalised versions of tooling developed at NIHR BioResource. No real participant data or internal paths are included.

---

## Overview

In a large biobank, samples are genotyped on different arrays over many years. When a researcher asks *"Do we have coverage for rs429358 across all our cohorts?"*, manually checking hundreds of PLINK files is impractical. This tool automates the audit.

**Capabilities:**
- **Deep recursive scan** — traverses complex directory structures to locate all `.bim` files.
- **Dual-mode lookup** — validates variants by rsID (`rs429358`) or GRCh38 coordinate (`19:44908684`).
- **Availability matrix** — generates a CSV showing exactly which arrays contain each queried variant.
- **Batch reporting** — summary statistics including per-array hit counts and overall availability rate.

## Repository Structure

```text
.
├── src/variant_explorer/       Python package
│   ├── __init__.py
│   ├── scanner.py              Core scanning engine
│   ├── batch.py                Batch checker with reporting
│   └── cli.py                  Command-line interface
├── tests/
│   ├── test_scanner.py
│   └── test_batch.py
├── legacy/                     Original scripts
│   ├── variant_scanner.py
│   └── batch_variant_check.sh
├── .github/workflows/ci.yml
├── pyproject.toml
├── Dockerfile
└── Makefile
```

## Quick Start

```bash
pip install -e ".[dev]"
```

### CLI

```bash
# Scan individual variants
variant-explorer scan --root-dir /data/genotypes --variants rs429358 rs7412

# Scan from CSV
variant-explorer scan --root-dir /data/genotypes --csv query.csv --output results.csv

# Batch check with summary report
variant-explorer batch --root-dir /data/genotypes --csv query.csv
```

### Python API

```python
from variant_explorer import VariantScanner, BatchChecker

scanner = VariantScanner("/data/genotypes")
print(scanner.arrays)           # ['CoreExome', 'GSA_v3', ...]

result = scanner.check_variant("rs429358")
print(result.is_available)      # True
print(result.array_count)       # 3

# Batch check
checker = BatchChecker(scanner)
report = checker.run_from_csv("query.csv")
print(checker.format_report(report))
```

## Testing

```bash
make test   # or: pytest tests/ -v
```

## Jira Provenance

- **SNP feasibility checking** — verifying variant availability across genotyping arrays before recall study design.
- **Cross-array auditing** — mapping which arrays and batches carry specific HLA and APOE markers.

## Licence

MIT
