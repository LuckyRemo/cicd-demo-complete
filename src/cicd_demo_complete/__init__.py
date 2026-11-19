"""Tiny text-statistics helpers used for the CI/CD demo."""

from .stats import Summary, count_words, reading_time_minutes, summarize, tokenize, top_words

__all__ = [
    "Summary",
    "count_words",
    "reading_time_minutes",
    "summarize",
    "tokenize",
    "top_words",
]

__version__ = "0.1.0"
