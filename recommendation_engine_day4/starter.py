"""
Day 4 - Customer Recommendation Engine
Squad Python Specialization - Data Science, AI & Analytics

Core Python only for the engine (csv, collections, math are fine). No ML libraries.
"""
from __future__ import annotations

import csv
from pathlib import Path

DATA_PATH = Path("data") / "purchases.csv"
OUTPUT_PATH = Path("output") / "recommendations.csv"


def read_purchases(path: Path = DATA_PATH) -> tuple[list[dict], list[dict]]:
    """Return (valid_rows, rejected_rows). Decide what makes a purchase row unusable."""
    raise NotImplementedError




if __name__ == "__main__":
    # TODO: build the engine, print recommendations for two customers, export all
    pass
