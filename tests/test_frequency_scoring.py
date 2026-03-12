import collections
from pathlib import Path

from src.core.frequency_scoring import compute_scores, load_global_freq


def test_compute_scores_prefers_common_and_local_words(tmp_path: Path):
    # Prepare a small global frequency CSV.
    csv_path = tmp_path / "freq.csv"
    csv_path.write_text(
        "word,rank,freq_per_million\n"
        "weekend,3500,50\n"
        "homework,7000,20\n",
        encoding="utf-8",
    )
    global_freq = load_global_freq(csv_path)

    counts = collections.Counter({"weekend": 4, "homework": 3})
    scored = compute_scores(counts, global_freq)
    # weekend should come before homework due to higher local count and better rank
    assert scored[0][0] == "weekend"
    assert scored[1][0] == "homework"

