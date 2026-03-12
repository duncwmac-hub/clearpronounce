from fastapi.testclient import TestClient

from src.backend.app import app, init_resources
from src.core.lexicon_service import LexEntry


def test_analyze_text_returns_ranked_vocab_with_pronunciation():
    # Prepare in-memory resources.
    global_freq = {"work": (1000, 100.0)}
    lexicon = {
        "work": LexEntry(
            word="work",
            ipa="w ɜːk",
            respelling="uerk",
            phoneme_set="{w, ɜː, k}",
            already_pronounceable=True,
            unlocked_by="",
        )
    }
    init_resources(global_freq, lexicon)

    client = TestClient(app)
    response = client.post("/analyze-text", json={"text": "Work work!"})
    assert response.status_code == 200

    data = response.json()
    assert "words" in data
    words = data["words"]
    assert len(words) >= 1

    top = words[0]
    assert top["word"] == "work"
    assert top["localCount"] == 2
    assert top["ipa"] == "w ɜːk"
    assert top["respelling"] == "uerk"

