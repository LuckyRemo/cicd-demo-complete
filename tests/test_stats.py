import pytest

from pycicd_demo.stats import (
    count_words,
    reading_time_minutes,
    summarize,
    tokenize,
    top_words,
)


def test_tokenize_ignores_punctuation_and_case():
    assert tokenize("Hello, hello! World... 42") == ["hello", "hello", "world", "42"]


def test_tokenize_keeps_apostrophes():
    assert tokenize("It's a test") == ["it's", "a", "test"]


def test_count_words():
    assert count_words("one two three") == 3
    assert count_words("") == 0


def test_top_words_orders_by_frequency():
    text = "apple banana apple cherry apple banana"
    assert top_words(text, limit=2) == [("apple", 3), ("banana", 2)]


@pytest.mark.parametrize("limit", [0, -1])
def test_top_words_rejects_bad_limit(limit):
    with pytest.raises(ValueError, match="limit"):
        top_words("anything", limit=limit)


def test_reading_time_rounds_to_two_decimals():
    assert reading_time_minutes("word " * 100, words_per_minute=200) == 0.5


def test_reading_time_rejects_bad_speed():
    with pytest.raises(ValueError, match="words_per_minute"):
        reading_time_minutes("text", words_per_minute=0)


def test_summarize_returns_immutable_top_words():
    summary = summarize("a b a c", top_n=2)
    assert summary.words == 4
    assert summary.unique_words == 3
    assert summary.reading_minutes == 0.02
    assert summary.top == (("a", 2), ("b", 1))


def test_summarize_rejects_bad_top_n():
    with pytest.raises(ValueError, match="top_n"):
        summarize("anything", top_n=0)
