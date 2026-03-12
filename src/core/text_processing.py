from __future__ import annotations

import collections
import re
from typing import Iterable, List


DEFAULT_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "if",
    "when",
    "while",
    "for",
    "to",
    "of",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "have",
    "has",
    "had",
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    "me",
    "him",
    "her",
    "them",
    "my",
    "your",
    "his",
    "their",
    "our",
    "this",
    "that",
    "these",
    "those",
}


WORD_RE = re.compile(r"[A-Za-z']+")


def normalise_text(text: str) -> str:
    """Basic normalisation: collapse whitespace, strip smart quotes."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(text.split())


def tokenise(text: str) -> List[str]:
    """Extract simple word-like tokens (letters and apostrophes)."""
    return WORD_RE.findall(text)


def normalise_token(token: str) -> str:
    """Lowercase and apply light suffix stripping for lemmas."""
    t = token.lower()

    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("ing") and len(t) > 4:
        return t[:-3]
    if t.endswith("ed") and len(t) > 3:
        return t[:-2]
    if t.endswith("es") and len(t) > 3:
        return t[:-2]
    if t.endswith("s") and len(t) > 3:
        return t[:-1]
    return t


def vocab_from_text(
    text: str,
    min_length: int = 2,
    stopwords: Iterable[str] = DEFAULT_STOPWORDS,
) -> collections.Counter:
    """Return lemma counts from text after normalisation and filtering."""
    stop = set(stopwords)
    norm = normalise_text(text)
    tokens = tokenise(norm)

    counts: collections.Counter = collections.Counter()
    for tok in tokens:
        lemma = normalise_token(tok)
        if len(lemma) < min_length:
            continue
        if lemma in stop:
            continue
        counts[lemma] += 1
    return counts

