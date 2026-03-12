#!/usr/bin/env python3
"""Text → vocab list prototype for ClearPronounce.

Given a block of English text (e.g. OCR output from a textbook photo),
this script normalises it, counts word frequencies, and prints a
frequency-ordered word list.

This is deliberately simple and designed as a first step before
integrating with the full ClearPronounce lexicon and unlocker.
"""

from __future__ import annotations

import argparse
import collections
from pathlib import Path
from typing import Dict, List, Tuple

from core.frequency_scoring import compute_scores, load_global_freq
from core.lexicon_service import load_lexicon
from core.text_processing import vocab_from_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert exercise text into a frequency-ordered vocab list. "
            "You can paste OCR output into a file and point this script at it."
        )
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a UTF-8 text file containing exercise text (e.g. from OCR).",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=2,
        help="Minimum lemma length to keep (default: 2).",
    )
    parser.add_argument(
        "--global-freq",
        type=Path,
        help="Optional CSV with columns word,rank,freq_per_million for global frequency ordering.",
    )
    parser.add_argument(
        "--lexicon",
        type=Path,
        help="Optional lexicon CSV with columns including word,ipa,polish_respellings to attach pronunciation data.",
    )
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    counts = vocab_from_text(text, min_length=args.min_length)

    global_freq: Dict[str, Tuple[int, float]] | None = None
    if args.global_freq:
        global_freq = load_global_freq(args.global_freq)

    scored = compute_scores(counts, global_freq)

    lex_mapping: Dict[str, Dict[str, str]] | None = None
    if args.lexicon:
        lex_mapping = load_lexicon(args.lexicon)

    # Print TSV header + rows.
    header_fields = [
        "word",
        "local_count",
        "global_rank",
        "global_freq_per_million",
        "score",
        "ipa",
        "polish_respellings",
    ]
    print("\t".join(header_fields))

    for word, local_count, rank, freq_pm, score in scored:
        rank_str = "" if rank is None else str(rank)
        freq_str = "" if freq_pm is None else f"{freq_pm:.3f}"
        ipa = ""
        resp = ""
        if lex_mapping is not None:
            row = lex_mapping.get(word)
            if row:
                ipa = (row.get("ipa") or "").strip()
                resp = (row.get("polish_respellings") or "").strip()
        print(f"{word}\t{local_count}\t{rank_str}\t{freq_str}\t{score:.6f}\t{ipa}\t{resp}")


if __name__ == "__main__":
    main()

