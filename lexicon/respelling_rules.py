#!/usr/bin/env python3
"""Loader for English → Polish respelling rules.

For now we treat rules/english_to_polish_respellings.md as the canonical,
human-edited source of truth. This module parses the markdown table into a
simple in-memory structure keyed by IPA phoneme.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class RespellingRule:
    english_phoneme: str
    default_letters: str
    notes: str


def _parse_table_line(line: str) -> RespellingRule | None:
    # Expect pipe-separated markdown row: | /p/ | p | ... | notes |
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return None
    # Skip header separator rows like |----|
    if set(line.replace("|", "").strip()) <= {"-", ":"}:
        return None

    parts = [part.strip() for part in line.split("|")[1:-1]]
    if len(parts) < 4:
        return None

    english_phoneme_raw, default_letters, _alternatives, notes = parts[:4]
    if not english_phoneme_raw:
        return None

    # Strip surrounding slashes from IPA field: "/p/" -> "p"
    english_phoneme = english_phoneme_raw.strip()
    if english_phoneme.startswith("/") and english_phoneme.endswith("/"):
        english_phoneme = english_phoneme[1:-1].strip()

    return RespellingRule(
        english_phoneme=english_phoneme,
        default_letters=default_letters,
        notes=notes,
    )


def load_respelling_rules(path: Path | str | None = None) -> Dict[str, RespellingRule]:
    """Load respelling rules from the markdown table into a dict.

    Keys are bare IPA phoneme strings, e.g. "tʃ", "ə", "eɪ".
    """
    if path is None:
        path = Path(__file__).resolve().parents[1] / "rules" / "english_to_polish_respellings.md"
    else:
        path = Path(path)

    rules: Dict[str, RespellingRule] = {}

    with path.open(encoding="utf-8") as f:
        for line in f:
            rule = _parse_table_line(line)
            if rule is None:
                continue
            if not rule.default_letters:
                continue
            rules[rule.english_phoneme] = rule

    return rules


def get_rule(phoneme: str, rules: Dict[str, RespellingRule] | None = None) -> RespellingRule | None:
    """Convenience accessor for a single phoneme."""
    if rules is None:
        rules = load_respelling_rules()
    return rules.get(phoneme)


__all__ = ["RespellingRule", "load_respelling_rules", "get_rule"]

