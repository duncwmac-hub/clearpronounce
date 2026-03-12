from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class LexEntry:
    word: str
    ipa: str
    respelling: str
    phoneme_set: str = ""
    already_pronounceable: Optional[bool] = None
    unlocked_by: str = ""


def load_lexicon(path: Path) -> Dict[str, LexEntry]:
    """Load a lexicon CSV keyed by word (lowercased)."""
    mapping: Dict[str, LexEntry] = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = (row.get("word") or "").strip().lower()
            if not word:
                continue
            ipa = (row.get("ipa") or "").strip()
            resp = (row.get("polish_respellings") or "").strip()
            phoneme_set = (row.get("phoneme_set") or "").strip()
            already_str = (row.get("already_pronounceable") or "").strip().lower()
            already: Optional[bool]
            if already_str == "yes":
                already = True
            elif already_str == "no":
                already = False
            else:
                already = None
            unlocked_by = (row.get("unlocked_by") or "").strip()
            mapping[word] = LexEntry(
                word=word,
                ipa=ipa,
                respelling=resp,
                phoneme_set=phoneme_set,
                already_pronounceable=already,
                unlocked_by=unlocked_by,
            )
    return mapping


def lookup(word: str, mapping: Dict[str, LexEntry]) -> Optional[LexEntry]:
    """Lookup a word in a loaded lexicon (case-insensitive)."""
    key = word.lower()
    return mapping.get(key)


