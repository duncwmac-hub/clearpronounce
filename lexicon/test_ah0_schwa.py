#!/usr/bin/env python3
"""Test whether AH0 should map to schwa (ə) or strut (ʌ).

Run from repo root:
  python -m lexicon.test_ah0_schwa

Then spot-check a few words in Cambridge Dictionary (or similar) and see whether
the unstressed vowel is written as ə or ʌ. If it's ə, we keep AH0 → ə.
"""

import csv
from pathlib import Path

from lexicon.ingest_cmudict import strip_stress, ARPABET_TO_IPA


def arpabet_to_ipa_with_ah(arpabet_pron: str, ah0_as_schwa: bool) -> str:
    """Convert ARPABET to IPA. AH0 can be ə (schwa) or ʌ (strut)."""
    phones = arpabet_pron.split()
    ipa_phones = []
    for p in phones:
        base = strip_stress(p)
        if base == "AH":
            if p.endswith("0"):
                ipa = "ə" if ah0_as_schwa else "ʌ"
            else:
                ipa = "ʌ"  # AH1, AH2 = strut
        else:
            ipa = ARPABET_TO_IPA.get(base)
        if ipa is None:
            ipa = f"<{base}>"
        ipa_phones.append(ipa)
    return " ".join(ipa_phones)


def main() -> None:
    base = Path(__file__).resolve().parent
    lexicon_path = base / "lexicon_oxford3000.csv"
    if not lexicon_path.exists():
        print("Lexicon not found at", lexicon_path)
        return

    # Collect words that contain AH0
    rows = []
    with lexicon_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cmu = (row.get("cmu_pron") or "").strip()
            if "AH0" in cmu:
                word = (row.get("word") or "").strip()
                if word:
                    ipa_schwa = arpabet_to_ipa_with_ah(cmu, ah0_as_schwa=True)
                    ipa_strut = arpabet_to_ipa_with_ah(cmu, ah0_as_schwa=False)
                    rows.append((word, cmu, ipa_schwa, ipa_strut))

    # Show first 30 so you can spot-check in a dictionary
    print("Words containing AH0 (unstressed). Spot-check in Cambridge Dictionary:")
    print("  https://dictionary.cambridge.org/dictionary/english/<word>")
    print()
    print(f"{'Word':<18} {'If AH0=ə (schwa)':<35} {'If AH0=ʌ (strut)'}")
    print("-" * 90)
    for word, cmu, ipa_schwa, ipa_strut in rows[:30]:
        diff = "  ← same" if ipa_schwa == ipa_strut else ""
        print(f"{word:<18} {ipa_schwa:<35} {ipa_strut}{diff}")
    print()
    print("If the dictionary shows ə for the unstressed vowel, use AH0 → ə (current behaviour).")
    print("Total words with AH0 in lexicon:", len(rows))


if __name__ == "__main__":
    main()
