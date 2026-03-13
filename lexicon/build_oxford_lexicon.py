#!/usr/bin/env python3
"""Build an Oxford 3000 lexicon with IPA, phoneme_set, and respellings.

This script reads the Oxford 3000 CSV from data/Oxford3000_Vocab-main/,
looks up pronunciations in CMUdict, converts them to IPA using the same
helpers as ingest_cmudict.py, and writes a lexicon-style CSV that can be
fed into the unlocker.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict

from .ingest_cmudict import arpabet_to_ipa, phoneme_set_from_ipa, load_cmudict
from .respeller import generate_respelling


def load_oxford_levels(path: Path | None) -> Dict[str, str]:
    """Load an optional word -> level mapping (e.g. A1, A2, B1).

    If no path is provided, returns an empty mapping and all words will get
    level "unknown" in the output.
    """
    levels: Dict[str, str] = {}
    if path is None or not path.exists():
        return levels

    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = (row.get("word") or row.get("Word") or "").strip().lower()
            level = (row.get("level") or row.get("Level") or "").strip()
            if not word or not level:
                continue
            levels[word] = level
    return levels


def build_oxford_lexicon(
    oxford_csv: Path,
    cmu_path: Path,
    out_path: Path,
    levels_path: Path | None = None,
) -> None:
    cmu = load_cmudict(cmu_path)
    levels = load_oxford_levels(levels_path)

    with oxford_csv.open(encoding="utf-8") as f_in, out_path.open(
        "w", newline="", encoding="utf-8"
    ) as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        writer.writerow(
            [
                "word",
                "ipa",
                "cmu_pron",
                "phoneme_set",
                "polish_respellings",
                "pos",
                "frequency_rank",
                "level",
                "definition",
                "example_sentence",
            ]
        )

        freq = 1
        for row in reader:
            word_raw = (row.get("Word") or "").strip()
            if not word_raw:
                continue
            word = word_raw.lower()
            if " " in word or "-" in word:
                # Skip multi-word and hyphenated expressions in this first pass.
                continue

            variants = cmu.get(word)
            if not variants:
                continue
            # For the static Oxford 3000 lexicon we keep the first CMU variant
            # as the default; runtime code can choose others using POS.
            cmu_pron = variants[0]

            ipa = arpabet_to_ipa(cmu_pron)
            phoneme_set = phoneme_set_from_ipa(ipa)
            respelling = generate_respelling(ipa)
            pos = (row.get("Part of Speech") or "").strip()
            definition = (row.get("Definition") or "").strip()
            example = (row.get("Example Sentence") or "").strip()
            level = levels.get(word, "unknown")

            writer.writerow(
                [
                    word,
                    ipa,
                    cmu_pron,
                    phoneme_set,
                    respelling,
                    pos,
                    freq,
                    level,
                    definition,
                    example,
                ]
            )
            freq += 1


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Build an Oxford 3000 lexicon CSV with IPA and respellings."
    )
    parser.add_argument(
        "--oxford",
        type=Path,
        required=True,
        help="Path to Oxford 3000 CSV (with a Word column)",
    )
    parser.add_argument(
        "--cmudict",
        type=Path,
        required=True,
        help="Path to CMUdict file (cmudict-0.7b format)",
    )
    parser.add_argument(
        "--levels",
        type=Path,
        required=False,
        help="Optional path to levels CSV with columns word,level",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output lexicon CSV path",
    )

    args = parser.parse_args()
    build_oxford_lexicon(args.oxford, args.cmudict, args.out, args.levels)


if __name__ == "__main__":
    main()

