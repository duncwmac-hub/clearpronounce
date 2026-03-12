from __future__ import annotations

import collections
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple


def load_global_freq(path: Path) -> Dict[str, Tuple[int, float]]:
    """Load global frequencies from a CSV (word,rank,freq_per_million)."""
    mapping: Dict[str, Tuple[int, float]] = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = (row.get("word") or "").strip().lower()
            if not word:
                continue
            try:
                rank = int(row.get("rank", "") or 0)
            except ValueError:
                rank = 0
            try:
                freq = float(row.get("freq_per_million", "") or 0.0)
            except ValueError:
                freq = 0.0
            mapping[word] = (rank, freq)
    return mapping


def compute_scores(
    counts: collections.Counter,
    global_freq: Dict[str, Tuple[int, float]] | None = None,
) -> List[Tuple[str, int, int | None, float | None, float]]:
    """Combine local counts with optional global frequency into a score.

    Returns a list of tuples:
    (word, local_count, global_rank, global_freq_per_million, score)
    """
    total_tokens = sum(counts.values()) or 1
    max_local = max(counts.values()) or 1

    scored: List[Tuple[str, int, int | None, float | None, float]] = []

    for word, local_count in counts.items():
        rank: int | None = None
        freq_pm: float | None = None
        global_usefulness = 0.0
        salience = 0.0

        if global_freq is not None and word in global_freq:
            rank, freq_pm = global_freq[word]
            if rank and rank > 0:
                global_usefulness = 1.0 / (1.0 + math.log(1.0 + rank))
            if freq_pm and freq_pm > 0:
                local_prop = local_count / total_tokens
                baseline = freq_pm / 1_000_000.0
                salience = min(local_prop / baseline, 5.0)

        local_norm = local_count / max_local
        score = 0.5 * global_usefulness + 0.3 * local_norm + 0.2 * salience

        scored.append((word, local_count, rank, freq_pm, score))

    scored.sort(key=lambda x: (-x[4], x[0]))
    return scored

