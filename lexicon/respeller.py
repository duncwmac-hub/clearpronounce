#!/usr/bin/env python3
"""First-pass IPA → Polish respelling generator."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .respelling_rules import load_respelling_rules


def tokenize_ipa(ipa: str) -> List[str]:
    """Tokenize an IPA string into phonemes.

    We assume:
    - Affricates and diphthongs arrive as single space-separated tokens from
      arpabet_to_ipa (e.g. "tʃ", "eɪ").
    - No need for further segmentation here.
    """
    return [p for p in ipa.split() if p]


def generate_respelling(ipa: str) -> str:
    """Generate a single canonical Polish-like respelling for a word.

    Uses the default_letters from rules/english_to_polish_respellings.md
    via the respelling_rules loader.
    """
    rules = load_respelling_rules()
    phones = tokenize_ipa(ipa)

    pieces: List[str] = []
    for phoneme in phones:
        rule = rules.get(phoneme)
        if rule is None:
            # Fall back to the raw phoneme if we have no mapping yet.
            pieces.append(phoneme)
        else:
            pieces.append(rule.default_letters)
    return "".join(pieces)


__all__ = ["tokenize_ipa", "generate_respelling"]

