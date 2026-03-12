#!/usr/bin/env python3
"""Rebuild polish_respellings in lexicon_oxford3000.csv from IPA.

This lets us pick up changes in rules/english_to_polish_respellings.md
(/ʌ/ -> â, etc.) without re-ingesting CMU + frequency.
"""

from __future__ import annotations

import csv
from pathlib import Path

from lexicon.respeller import generate_respelling


def main() -> None:
    base = Path(__file__).resolve().parent
    lex_path = base / "lexicon_oxford3000.csv"
    out_path = base / "lexicon_oxford3000_updated.csv"

    if not lex_path.exists():
        print("Lexicon not found at", lex_path)
        return

    with lex_path.open(encoding="utf-8") as f_in, out_path.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames or []
        if "polish_respellings" not in fieldnames:
            print("No polish_respellings column found; aborting.")
            return

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            ipa = (row.get("ipa") or "").strip()
            if ipa:
                row["polish_respellings"] = generate_respelling(ipa)
            writer.writerow(row)

    out_path.rename(lex_path)
    print("Updated polish_respellings in", lex_path)


if __name__ == "__main__":
    main()

