from src.core.text_processing import normalise_text, tokenise, normalise_token, vocab_from_text


def test_normalise_text_collapses_whitespace_and_quotes():
    text = "He\u00a0said\u00a0\u201cHello\u201d  to  her."
    assert normalise_text(text) == 'He said "Hello" to her.'


def test_tokenise_extracts_words_and_apostrophes():
    text = "It's time to work."
    assert tokenise(text) == ["It", "s", "time", "to", "work"]


def test_normalise_token_applies_simple_lemmatisation():
    assert normalise_token("studies") == "study"
    assert normalise_token("working") == "work"
    assert normalise_token("worked") == "work"
    assert normalise_token("watches") == "watch"
    assert normalise_token("books") == "book"


def test_vocab_from_text_counts_filtered_lemmas():
    text = "He is working and she worked. They work together."
    counts = vocab_from_text(text, min_length=3)
    # stopwords like he, is, and, she, they should be removed
    assert counts["work"] == 3

