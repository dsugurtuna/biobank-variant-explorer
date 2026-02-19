#!/usr/bin/env python3
"""
Biobank Variant Scanner
=======================

A bioinformatics utility to search for specific genetic variants (rsIDs or genomic coordinates)
across multiple PLINK binary datasets (.bim files) in a high-performance computing environment.

Features:
- Recursive search for .bim files in specified directories.
- Validates presence of variants using rsID or GRCh38 coordinates.
- Generates a comprehensive CSV report of variant availability across arrays.

Author:      Ugur Tuna
Context:     Developed during tenure at NIHR BioResource (Cambridge).
Disclaimer:  Sanitized version for educational/portfolio use.
"""

import os
import sys
import subprocess
import pandas as pd
import argparse
from typing import List, Tuple, Optional

# ==============================================================================
# Configuration
# ==============================================================================

# Default search paths (Sanitized for public release)
# In a real environment, these would be specific HPC paths.
DEFAULT_ROOT_DIR = "/path/to/biobank/processed/data"

# Standard Biobank Genotyping Arrays/Directories to search
DEFAULT_SEARCH_DIRS = [
    "4EGA",
    "Affy-BIOAXIOMAX",
    "Affy-INTERVALAX",
    "Genotypes",
    "TF-UKBBV2.1",
    "UKBBv2_2",
    "PLINK",
    "IBD"
]

def parse_args():
    parser = argparse.ArgumentParser(description="Search for variants in PLINK datasets.")
    parser.add_argument("--input", "-i", required=True, help="Input CSV file containing variants.")
    parser.add_argument("--output", "-o", default="variant_search_results.csv", help="Output CSV file.")
    parser.add_argument("--root-dir", default=DEFAULT_ROOT_DIR, help="Root directory to search for genotype data.")
    return parser.parse_args()

def find_bim_files(root_dir: str, subdirs: List[str]) -> List[str]:
    """Find all PLINK bim files in the data directory."""
    print(f"Searching for BIM files in {root_dir}...")
    
    bim_files = []
    
    for search_dir in subdirs:
        full_path = os.path.join(root_dir, search_dir)
        if not os.path.exists(full_path):
            print(f"Warning: Directory {full_path} not found (Skipping)")
            continue
        
        # Use find command to locate BIM files efficiently
        cmd = f"find {full_path} -name '*.bim'"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            found_files = [f for f in result.stdout.strip().split('\n') if f]
            print(f"  Found {len(found_files)} BIM files in {search_dir}")
            bim_files.extend(found_files)
        except subprocess.CalledProcessError as e:
            print(f"  Error searching {search_dir}: {e}")
            
    return bim_files

def check_variant_in_bim(bim_file: str, rsid: Optional[str], coordinate: Optional[str]) -> Tuple[bool, str]:
    """
    Check if a variant is present in a BIM file using grep/awk for speed.
    Returns (found_boolean, details_string).
    """
    # 1. Check by rsID (e.g., rs429358)
    if rsid and str(rsid).startswith("rs"):
        # grep -w matches whole words only
        cmd = f"grep -w '{rsid}' '{bim_file}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return True, result.stdout.strip()
    
    # 2. Check by Coordinate (e.g., 19:45411941)
    if coordinate and ":" in str(coordinate):
        try:
            chr_num, pos = str(coordinate).split(":")
            # AWK check: Column 1 is Chr, Column 4 is Pos
            cmd = f"awk '$1 == \"{chr_num}\" && $4 == {pos}' '{bim_file}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                return True, result.stdout.strip()
        except ValueError:
            pass # Malformed coordinate
    
    return False, ""

def main():
    args = parse_args()
    
    # Validate Input
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        sys.exit(1)
    
    # 1. Locate Datasets
    bim_files = find_bim_files(args.root_dir, DEFAULT_SEARCH_DIRS)
    print(f"Total BIM files to scan: {len(bim_files)}")
    
    if not bim_files:
        print("Error: No BIM files found. Check your --root-dir path.")
        sys.exit(1)

    # 2. Load Variants
    try:
        variants_df = pd.read_csv(args.input)
        print(f"Loaded {len(variants_df)} variants from input.")
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    if variants_df.empty:
        print("No variants found in the input file.")
        sys.exit(0)
    
    # 3. Scan Variants
    results = []
    
    for idx, variant in variants_df.iterrows():
        # Flexible column naming handling
        rsid = variant.get('dbSNP ID') or variant.get('rsid') or variant.get('SNP')
        coordinate = variant.get('Coordinate (GRCh38.p13)') or variant.get('Coordinate') or variant.get('pos')
        
        if pd.isna(rsid) and pd.isna(coordinate):
            continue

        print(f"[{idx+1}/{len(variants_df)}] Checking: rsID={rsid}, Coord={coordinate}")
        
        variant_info = variant.to_dict()
        arrays_present = []
        
        for bim_file in bim_files:
            # Extract array name from parent directory
            array_name = os.path.basename(os.path.dirname(bim_file))
            
            is_present, details = check_variant_in_bim(bim_file, rsid, coordinate)
            
            if is_present:
                arrays_present.append(array_name)
                variant_info[f'Found_In_{array_name}'] = "Yes"
                variant_info[f'Details_{array_name}'] = details
            
        variant_info['Summary_Arrays_Present'] = ", ".join(arrays_present) if arrays_present else "None"
        results.append(variant_info)
    
    # 4. Save Results
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv(args.output, index=False)
        print(f"\n[SUCCESS] Results saved to {args.output}")
    else:
        print("\n[INFO] No results generated.")

if __name__ == "__main__":
    main()
