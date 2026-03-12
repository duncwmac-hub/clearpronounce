from pathlib import Path

from src.core.lexicon_service import LexEntry, load_lexicon, lookup


def test_load_lexicon_and_lookup(tmp_path: Path):
    csv_path = tmp_path / "lexicon.csv"
    csv_path.write_text(
        "word,ipa,polish_respellings,phoneme_set,already_pronounceable,unlocked_by\n"
        "work,w ɜːk,uerk,\"{w, ɜː, k}\",yes,\n",
        encoding=\"utf-8\",
    )
    mapping = load_lexicon(csv_path)
    entry = lookup(\"work\", mapping)
    assert isinstance(entry, LexEntry)
    assert entry.ipa == \"w ɜːk\"
    assert entry.respelling == \"uerk\"
    assert entry.already_pronounceable is True

