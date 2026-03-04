"""Tests for the summarizer module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.news_fetcher import NewsItem
from src.summarizer import summarize_news, _build_user_message


def _make_items(n: int = 3) -> list[NewsItem]:
    return [
        NewsItem(
            title=f"Article {i}",
            url=f"https://example.com/{i}",
            source="Test Source",
            summary=f"Summary of article {i}",
        )
        for i in range(n)
    ]


class TestBuildUserMessage:
    def test_contains_titles(self):
        items = _make_items(2)
        msg = _build_user_message(items)
        assert "Article 0" in msg
        assert "Article 1" in msg

    def test_numbered_lines(self):
        items = _make_items(3)
        msg = _build_user_message(items)
        assert msg.startswith("1.")


class TestSummarizeNews:
    def test_skips_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        items = _make_items(2)
        result = summarize_news(items, api_key="")
        for item in result:
            assert item.ai_summary == ""

    def test_sets_ai_summary(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        items = _make_items(2)

        mock_message = MagicMock()
        mock_message.content = "Insight for article 0.\nInsight for article 1."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.summarizer.OpenAI", return_value=mock_client):
            result = summarize_news(items, api_key="test-key")

        assert result[0].ai_summary == "Insight for article 0."
        assert result[1].ai_summary == "Insight for article 1."

    def test_strips_leading_numbering(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        items = _make_items(1)

        mock_message = MagicMock()
        mock_message.content = "1. This is the insight."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.summarizer.OpenAI", return_value=mock_client):
            result = summarize_news(items, api_key="test-key")

        assert result[0].ai_summary == "This is the insight."

    def test_batching(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        items = _make_items(5)

        mock_message = MagicMock()
        mock_message.content = "\n".join(f"Insight {i}." for i in range(3))
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.summarizer.OpenAI", return_value=mock_client):
            summarize_news(items, api_key="test-key", batch_size=3)

        # Should have been called twice (batch of 3 + batch of 2)
        assert mock_client.chat.completions.create.call_count == 2
