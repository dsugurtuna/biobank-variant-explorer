"""Biobank Variant Explorer — high-throughput variant lookup across genotyping arrays."""

__version__ = "2.0.0"

from .scanner import VariantScanner, ScanResult
from .batch import BatchChecker

__all__ = ["VariantScanner", "ScanResult", "BatchChecker"]
