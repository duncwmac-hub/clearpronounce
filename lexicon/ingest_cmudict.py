#!/usr/bin/env python3
"""Ingest a subset of CMUdict + frequency list into lexicon_seed.csv-style rows.

This is deliberately small and idempotent: you specify paths and a max word count.
For now it only populates word, cmu_pron, ipa, phoneme_set, frequency_rank; respellings
can be added later by rules + manual tuning.
"""

import csv
from pathlib import Path

from .respeller import generate_respelling

# Minimal ARPABET -> IPA mapping for core vowels/consonants we care about now.
ARPABET_TO_IPA = {
    "P": "p", "B": "b", "T": "t", "D": "d", "K": "k", "G": "g",
    "CH": "tʃ", "JH": "dʒ", "F": "f", "V": "v", "TH": "θ", "DH": "ð",
    "S": "s", "Z": "z", "SH": "ʃ", "ZH": "ʒ", "HH": "h",
    "M": "m", "N": "n", "NG": "ŋ", "L": "l", "R": "r", "Y": "j", "W": "w",
    # Vowels (ignore stress digits for now)
    "IY": "i", "IH": "ɪ", "EY": "eɪ", "EH": "ɛ", "AE": "æ",
    "AA": "ɑ", "AO": "ɔ", "UH": "ʊ", "UW": "u", "AH": "ʌ", "ER": "ɝ",
    "AY": "aɪ", "OY": "ɔɪ", "AW": "aʊ", "OW": "oʊ",
}


def strip_stress(phone: str) -> str:
    """Remove stress digits from an ARPABET phone (e.g. 'AH0' -> 'AH')."""
    while phone and phone[-1].isdigit():
        phone = phone[:-1]
    return phone


def arpabet_to_ipa(arpabet_pron: str) -> str:
    """Convert ARPABET to IPA. AH0 (unstressed) -> schwa ə; AH1/AH2 -> ʌ."""
    phones = arpabet_pron.split()
    ipa_phones = []
    for p in phones:
        base = strip_stress(p)
        # Unstressed AH is schwa; stressed AH is strut.
        if base == "AH" and p.endswith("0"):
            ipa = "ə"
        else:
            ipa = ARPABET_TO_IPA.get(base)
        if ipa is None:
            ipa = f"<{base}>"
        ipa_phones.append(ipa)
    return " ".join(ipa_phones)


def phoneme_set_from_ipa(ipa: str) -> str:
    """Very simple phoneme set representation: split on spaces and wrap in {...}.

    In future we may want a smarter tokenizer for affricates etc., but here we
    assume affricates are already single tokens from arpabet_to_ipa.
    """
    phones = [p for p in ipa.split() if p]
    return "{" + ", ".join(sorted(set(phones))) + "}"


def load_frequency_ranks(path: Path) -> dict:
    """Load word -> frequency_rank from a CSV with columns word,frequency_rank."""
    ranks: dict[str, int] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row["word"].strip().lower()
            if not word:
                continue
            try:
                rank = int(row["frequency_rank"])
            except (KeyError, ValueError):
                continue
            if word not in ranks or rank < ranks[word]:
                ranks[word] = rank
    return ranks


def load_cmudict(path: Path) -> dict:
    """Load CMUdict-style file: WORD  PHON PHON ...

    Returns word -> list of ARPABET strings (we keep only the first for now).
    """
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(";;;"):
                continue
            parts = line.split()
            word = parts[0]
            # Strip possible (1), (2) variants.
            if "(" in word:
                word = word.split("(", 1)[0]
            word = word.lower()
            pron = " ".join(parts[1:])
            if word not in mapping:
                mapping[word] = pron
    return mapping


def ingest_subset(
    cmu_path: Path,
    freq_path: Path,
    out_path: Path,
    max_words: int = 500,
) -> None:
    freq_ranks = load_frequency_ranks(freq_path)
    cmu = load_cmudict(cmu_path)

    # Choose words by increasing frequency_rank.
    sorted_words = sorted(freq_ranks.items(), key=lambda x: x[1])[:max_words]

    with out_path.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow([
            "word",
            "ipa",
            "cmu_pron",
            "phoneme_set",
            "polish_respellings",
            "pos",
            "frequency_rank",
        ])
        for word, rank in sorted_words:
            cmu_pron = cmu.get(word)
            if not cmu_pron:
                continue
            ipa = arpabet_to_ipa(cmu_pron)
            phoneme_set = phoneme_set_from_ipa(ipa)
            polish_respellings = generate_respelling(ipa)
            writer.writerow([
                word,
                ipa,
                cmu_pron,
                phoneme_set,
                polish_respellings,
                "",
                rank,
            ])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest CMUdict + frequency list into lexicon CSV.")
    parser.add_argument("--cmudict", type=Path, required=True, help="Path to CMUdict file")
    parser.add_argument("--freq", type=Path, required=True, help="Path to frequency list CSV (word,frequency_rank)")
    parser.add_argument("--out", type=Path, required=True, help="Output CSV path")
    parser.add_argument("--max-words", type=int, default=500, help="Maximum number of words to ingest")

    args = parser.parse_args()
    ingest_subset(args.cmudict, args.freq, args.out, args.max_words)
