"""Pure functions that turn text into simple statistics."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

_WORD_RE = re.compile(r"[A-Za-z0-9']+")


@dataclass(frozen=True)
class Summary:
    """All statistics produced for one piece of text."""

    words: int
    unique_words: int
    reading_minutes: float
    top: tuple[tuple[str, int], ...]


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens, ignoring punctuation."""
    return [match.group(0).lower() for match in _WORD_RE.finditer(text)]


def count_words(text: str) -> int:
    """Return the number of word tokens in *text*."""
    return len(tokenize(text))


def top_words(text: str, limit: int = 5) -> list[tuple[str, int]]:
    """Return the *limit* most common words, most frequent first."""
    if limit < 1:
        raise ValueError("limit must be greater than or equal to 1")
    return Counter(tokenize(text)).most_common(limit)


def reading_time_minutes(text: str, words_per_minute: int = 200) -> float:
    """Estimate reading time in minutes, rounded to two decimals."""
    if words_per_minute <= 0:
        raise ValueError("words_per_minute must be greater than 0")
    return round(count_words(text) / words_per_minute, 2)


def summarize(text: str, top_n: int = 5) -> Summary:
    """Build a :class:`Summary` for *text*."""
    if top_n < 1:
        raise ValueError("top_n must be greater than or equal to 1")
    tokens = tokenize(text)
    unique = len(set(tokens))
    minutes = round(len(tokens) / 200, 2)
    return Summary(
        words=len(tokens),
        unique_words=unique,
        reading_minutes=minutes,
        top=tuple(Counter(tokens).most_common(top_n)),
    )
