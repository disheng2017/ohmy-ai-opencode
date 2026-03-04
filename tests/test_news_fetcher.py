"""Tests for the news_fetcher module."""

from __future__ import annotations

import textwrap
from unittest.mock import MagicMock, patch

import pytest

from src.news_fetcher import DEFAULT_SOURCES, NewsItem, fetch_news


def _make_entry(title: str, link: str, summary: str = "", published: str = "") -> MagicMock:
    entry = MagicMock()
    entry.get = lambda key, default="": {
        "title": title,
        "link": link,
    }.get(key, default)
    entry.summary = summary
    entry.published = published
    # Make hasattr work properly
    entry.configure_mock(**{"published": published})
    return entry


def _make_feed(entries):
    feed = MagicMock()
    feed.entries = entries
    return feed


class TestNewsItem:
    def test_str_with_ai_summary(self):
        item = NewsItem(
            title="GPT-5 Released",
            url="https://example.com/gpt5",
            source="Test Source",
            ai_summary="OpenAI has released GPT-5 with major improvements.",
        )
        text = str(item)
        assert "GPT-5 Released" in text
        assert "Test Source" in text
        assert "OpenAI has released GPT-5" in text

    def test_str_with_plain_summary(self):
        item = NewsItem(
            title="AI News",
            url="https://example.com/news",
            source="Test",
            summary="Some long summary text that will be truncated" * 10,
        )
        text = str(item)
        assert "AI News" in text
        assert "Summary:" in text

    def test_str_minimal(self):
        item = NewsItem(title="Title", url="https://x.com", source="Src")
        text = str(item)
        assert "Title" in text
        assert "URL: https://x.com" in text


class TestFetchNews:
    def test_returns_news_items(self):
        entry = _make_entry(
            "Test AI Article",
            "https://example.com/article",
            summary="Summary text",
            published="Mon, 01 Jan 2024 00:00:00 +0000",
        )
        mock_feed = _make_feed([entry])

        with patch("src.news_fetcher.feedparser.parse", return_value=mock_feed):
            items = fetch_news(
                sources=[{"name": "Test Source", "url": "https://example.com/feed"}],
                max_per_source=5,
            )

        assert len(items) == 1
        assert items[0].title == "Test AI Article"
        assert items[0].source == "Test Source"
        assert items[0].url == "https://example.com/article"

    def test_respects_max_per_source(self):
        entries = [
            _make_entry(f"Article {i}", f"https://example.com/{i}")
            for i in range(10)
        ]
        mock_feed = _make_feed(entries)

        with patch("src.news_fetcher.feedparser.parse", return_value=mock_feed):
            items = fetch_news(
                sources=[{"name": "Source", "url": "https://example.com/feed"}],
                max_per_source=3,
            )

        assert len(items) == 3

    def test_uses_default_sources_when_none_given(self):
        mock_feed = _make_feed([])
        with patch("src.news_fetcher.feedparser.parse", return_value=mock_feed) as mock_parse:
            fetch_news()
        assert mock_parse.call_count == len(DEFAULT_SOURCES)

    def test_strips_html_from_summary(self):
        entry = _make_entry(
            "Article",
            "https://example.com",
            summary="<p>Some <b>bold</b> text</p>",
        )
        mock_feed = _make_feed([entry])

        with patch("src.news_fetcher.feedparser.parse", return_value=mock_feed):
            items = fetch_news(
                sources=[{"name": "S", "url": "https://example.com/feed"}]
            )

        assert "<" not in items[0].summary
        assert "bold" in items[0].summary

    def test_multiple_sources_aggregated(self):
        mock_feed = _make_feed([_make_entry("Article", "https://example.com")])
        with patch("src.news_fetcher.feedparser.parse", return_value=mock_feed):
            items = fetch_news(
                sources=[
                    {"name": "A", "url": "https://a.com/feed"},
                    {"name": "B", "url": "https://b.com/feed"},
                ]
            )
        assert len(items) == 2
        sources = {i.source for i in items}
        assert sources == {"A", "B"}
