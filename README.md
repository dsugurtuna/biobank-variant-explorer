# Biobank Variant Explorer 🧬

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/Language-Bash-blue.svg)](https://www.gnu.org/software/bash/)
[![Bioinformatics](https://img.shields.io/badge/Domain-Bioinformatics-green.svg)]()
[![Portfolio](https://img.shields.io/badge/Status-Portfolio_Project-purple.svg)]()

**High-Throughput Variant Discovery Tool for Biobank Genotyping Arrays.**

> **Note:** This repository contains sanitized versions of scripts developed during my tenure at **NIHR BioResource**. They are presented here for **educational and portfolio purposes only** to demonstrate proficiency in data quality control and bioinformatics tool development. No real patient data or internal infrastructure paths are included.

The **Biobank Variant Explorer** is a specialized utility designed to audit large-scale genomic data lakes. It recursively scans PLINK binary datasets (`.bim` files) to verify the presence of specific genetic variants across different genotyping arrays and batches.

---

## 🌟 Use Case: Data Quality & Availability

In a large biobank, samples are often genotyped on different arrays (e.g., Affymetrix, Illumina) over many years. When a researcher asks:
> *"Do we have coverage for this specific rare variant (rs12345) across all our cohorts?"*

Manually checking hundreds of PLINK files is impossible. This tool automates the audit, providing a clear "Yes/No" map of variant availability.

## 🚀 Key Features

*   **🔍 Deep Recursive Scan**: Traverses complex directory structures to locate all available PLINK datasets.
*   **⚡ Hybrid Search**: Uses Python for logic and optimized system calls (`grep`/`awk`) for high-speed file parsing.
*   **📍 Dual-Mode Lookup**: Validates variants by **rsID** (e.g., `rs429358`) OR **Genomic Coordinate** (e.g., `19:45411941`).
*   **📊 Audit Reports**: Generates detailed CSV matrices showing exactly which arrays contain the target variants.

## 📂 Repository Structure

```text
.
├── variant_scanner.py      # 🧠 Core Logic: The search engine
├── batch_variant_check.sh  # 🚀 Wrapper: Easy batch execution script
├── requirements.txt        # 📦 Dependencies
└── README.md               # 📖 Documentation
```

## 🛠️ Usage

### Prerequisites
*   Python 3.8+
*   Standard Unix tools (`grep`, `awk`, `find`)

### 1. Prepare Input
Create a CSV file with your variants of interest:
```csv
dbSNP ID,Coordinate (GRCh38.p13)
rs429358,19:45411941
rs7412,19:45412079
```

### 2. Run the Scan
```bash
# Set your data root (optional, defaults to config)
export BIOBANK_DATA_ROOT="/path/to/your/genotypes"

# Run the batch check
./batch_variant_check.sh my_variants.csv
```

### 3. View Results
The tool outputs a CSV detailing availability:
| dbSNP ID | Found_In_Affy | Found_In_Illumina | Details_Affy |
| :--- | :--- | :--- | :--- |
| rs429358 | Yes | No | 19 rs429358 0 45411941 T C |

## 🤝 Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---
*Developed to ensure data integrity and accessibility in large-scale genomic research.*
