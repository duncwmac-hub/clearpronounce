#!/usr/bin/env python3
"""Unlocker logic for Polish vs English phoneme inventories.

Given:
- Polish phoneme set P (from rules/phonemes_polish.md)
- English phoneme set E (from rules/phonemes_english.md)
- A lexicon CSV with a phoneme_set column like "{ð, ə}"

We compute, for each word:
- whether its phoneme set is already a subset of P ("already_pronounceable"), and
- for each candidate new phoneme x in (E \ P), whether the word becomes pronounceable
  with P ∪ {x} but not with P alone ("unlocked_by").

Outputs a small report CSV for analysis/visualisation.
"""

from __future__ import annotations

import csv
from pathlib import Path


def parse_set_field(s: str) -> set[str]:
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    if not s:
        return set()
    return {item.strip() for item in s.split(",") if item.strip()}


def load_inventory(path: Path) -> set[str]:
    """Load a phoneme inventory from a markdown file by scraping the first line with '/'...'/'.

    This is intentionally simple: we look for the first non-empty line that starts with '/' and
    ends with '/'.
    """
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("/") and line.endswith("/"):
                inner = line[1:-1]
                return {p.strip() for p in inner.split(",") if p.strip()}
    raise ValueError(f"Could not find inventory line in {path}")


def compute_unlocks(
    lexicon_path: Path,
    english_inventory_path: Path,
    polish_inventory_path: Path,
    out_report_path: Path,
) -> None:
    E = load_inventory(english_inventory_path)
    P = load_inventory(polish_inventory_path)

    new_phonemes = sorted(E - P)

    with lexicon_path.open(newline="", encoding="utf-8") as f_in, out_report_path.open(
        "w", newline="", encoding="utf-8"
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames or []) + [
            "already_pronounceable",
            "unlocked_by",  # semicolon-separated list of phonemes
        ]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            phoneme_set = parse_set_field(row.get("phoneme_set", ""))
            already = phoneme_set.issubset(P)

            unlocked_by: list[str] = []
            if not already:
                for x in new_phonemes:
                    if phoneme_set.issubset(P | {x}) and not phoneme_set.issubset(P):
                        unlocked_by.append(x)

            row["already_pronounceable"] = "yes" if already else "no"
            row["unlocked_by"] = ";".join(unlocked_by)
            writer.writerow(row)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compute unlocker statistics for lexicon vs Polish inventory.")
    parser.add_argument("--lexicon", type=Path, required=True, help="Input lexicon CSV (with phoneme_set column)")
    parser.add_argument("--english", type=Path, required=True, help="English phoneme inventory markdown")
    parser.add_argument("--polish", type=Path, required=True, help="Polish phoneme inventory markdown")
    parser.add_argument("--out", type=Path, required=True, help="Output report CSV path")

    args = parser.parse_args()
    compute_unlocks(args.lexicon, args.english, args.polish, args.out)
