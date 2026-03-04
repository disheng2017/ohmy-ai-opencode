"""Tests for the agent module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.agent import _parse_args, run
from src.news_fetcher import NewsItem


def _make_item(title: str = "Test", source: str = "S") -> NewsItem:
    return NewsItem(title=title, url="https://example.com", source=source)


class TestParseArgs:
    def test_defaults(self):
        args = _parse_args([])
        assert args.max_per_source == 5
        assert args.use_ai is True
        assert args.sources is None
        assert args.output is None

    def test_no_ai_flag(self):
        args = _parse_args(["--no-ai"])
        assert args.use_ai is False

    def test_max_flag(self):
        args = _parse_args(["--max", "10"])
        assert args.max_per_source == 10


class TestRun:
    def test_run_without_ai(self, capsys):
        items = [_make_item("Article One"), _make_item("Article Two")]
        with patch("src.agent.fetch_news", return_value=items) as mock_fetch, \
             patch("src.agent.summarize_news") as mock_sum:
            result = run(use_ai=False)

        mock_fetch.assert_called_once()
        mock_sum.assert_not_called()
        assert len(result) == 2
        captured = capsys.readouterr()
        assert "Article One" in captured.out

    def test_run_with_ai(self, capsys):
        items = [_make_item("AI Article")]
        with patch("src.agent.fetch_news", return_value=items), \
             patch("src.agent.summarize_news", return_value=items) as mock_sum:
            run(use_ai=True, api_key="test-key")

        mock_sum.assert_called_once()

    def test_run_writes_json_output(self, tmp_path, capsys):
        items = [_make_item("Article")]
        out_file = str(tmp_path / "out.json")
        with patch("src.agent.fetch_news", return_value=items), \
             patch("src.agent.summarize_news", return_value=items):
            run(use_ai=True, output_file=out_file)

        import json
        with open(out_file) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "Article"
