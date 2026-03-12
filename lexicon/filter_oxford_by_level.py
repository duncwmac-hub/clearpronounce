#!/usr/bin/env python3
"""Filter Oxford unlocker output to A1 Polish-pronounceable words."""

from __future__ import annotations

import csv
from pathlib import Path


def filter_a1_pronounceable(
    unlocks_path: Path,
    out_path: Path,
    level: str = "A1",
) -> None:
    with unlocks_path.open(encoding="utf-8") as f_in, out_path.open(
        "w", newline="", encoding="utf-8"
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames or []
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row.get("level") != level:
                continue
            if row.get("already_pronounceable") != "yes":
                continue
            writer.writerow(row)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Filter Oxford unlocker CSV to A1 Polish-pronounceable words."
    )
    parser.add_argument(
        "--unlocks",
        type=Path,
        required=True,
        help="Path to lexicon_oxford3000_unlocks.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output CSV path for A1 pronounceable words",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="A1",
        help="CEFR level to filter on (default: A1)",
    )

    args = parser.parse_args()
    filter_a1_pronounceable(args.unlocks, args.out, args.level)


if __name__ == "__main__":
    main()

