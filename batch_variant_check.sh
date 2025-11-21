#!/bin/bash

# ==============================================================================
# Script Name: batch_variant_check.sh
# Author:      Ugur Tuna
# Context:     Developed during tenure at NIHR BioResource (Cambridge).
# Disclaimer:  Sanitized version for educational/portfolio use.
#
# Description: A wrapper script to process a batch of variants from a CSV file.
#              It validates the input and calls the Python scanner.
# Usage:       ./batch_variant_check.sh <variants.csv>
# ==============================================================================

# --- Configuration ---
# Path to the Python scanner script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCANNER="$SCRIPT_DIR/variant_scanner.py"

# Set the root directory for your data (Override this or set via env var)
DATA_ROOT="${BIOBANK_DATA_ROOT:-/path/to/biobank/processed/data}"

# --- Validation ---

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <variants.csv>"
    echo "Example: $0 my_gene_variants.csv"
    exit 1
fi

INPUT_CSV=$1

if [ ! -f "$INPUT_CSV" ]; then
    echo "Error: Input file '$INPUT_CSV' not found."
    exit 1
fi

if [ ! -f "$PYTHON_SCANNER" ]; then
    echo "Error: Python scanner script not found at $PYTHON_SCANNER"
    exit 1
fi

# --- Execution ---

echo "========================================================"
echo "Biobank Variant Batch Check"
echo "Input File: $INPUT_CSV"
echo "Data Root:  $DATA_ROOT"
echo "========================================================"

# Run the Python scanner
python3 "$PYTHON_SCANNER" \
    --input "$INPUT_CSV" \
    --output "results_$(basename "$INPUT_CSV")" \
    --root-dir "$DATA_ROOT"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "========================================================"
    echo "Batch check completed successfully."
    echo "Results saved to: results_$(basename "$INPUT_CSV")"
    echo "========================================================"
else
    echo "========================================================"
    echo "Error: Variant scan failed with exit code $EXIT_CODE"
    echo "========================================================"
    exit $EXIT_CODE
fi
