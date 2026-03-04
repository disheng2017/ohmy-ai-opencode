"""
AI News Agent – main entry point.

Usage
-----
    python -m src.agent [--sources sources.json] [--max N] [--no-ai] [--output FILE]

Environment variables
---------------------
    OPENAI_API_KEY   Required for AI summarisation (skipped when absent).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import List

from dotenv import load_dotenv

from .news_fetcher import DEFAULT_SOURCES, NewsItem, fetch_news
from .summarizer import summarize_news

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run(
    sources: List[dict] | None = None,
    max_per_source: int = 5,
    use_ai: bool = True,
    output_file: str | None = None,
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
) -> List[NewsItem]:
    """Fetch AI news and optionally enrich with AI summaries.

    Args:
        sources: RSS feed sources.  Defaults to :data:`~news_fetcher.DEFAULT_SOURCES`.
        max_per_source: Max articles to fetch per source.
        use_ai: Whether to call the OpenAI API for summaries.
        output_file: If given, write JSON output to this path.
        api_key: OpenAI API key.  Falls back to ``OPENAI_API_KEY`` env var.
        model: OpenAI model name used for summarisation.

    Returns:
        List of enriched :class:`~news_fetcher.NewsItem` objects.
    """
    logger.info("Fetching AI news…")
    items = fetch_news(sources=sources, max_per_source=max_per_source)

    if use_ai:
        logger.info("Generating AI summaries…")
        items = summarize_news(items, api_key=api_key, model=model)

    # ── Print to stdout ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  AI News Digest  –  {len(items)} articles")
    print(f"{'='*60}\n")
    for item in items:
        print(item)
        print()

    # ── Optional JSON export ─────────────────────────────────────────────────
    if output_file:
        data = [
            {
                "title": it.title,
                "url": it.url,
                "source": it.source,
                "published": it.published,
                "summary": it.summary,
                "ai_summary": it.ai_summary,
            }
            for it in items
        ]
        with open(output_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        logger.info("Results written to %s", output_file)

    return items


def _parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI News Agent – fetch and summarise the latest AI news."
    )
    parser.add_argument(
        "--sources",
        metavar="FILE",
        help="Path to a JSON file with custom RSS sources "
             "(list of {name, url} objects). Defaults to built-in sources.",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=5,
        dest="max_per_source",
        metavar="N",
        help="Max articles per source (default: 5).",
    )
    parser.add_argument(
        "--no-ai",
        action="store_false",
        dest="use_ai",
        help="Skip OpenAI summarisation.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write results to a JSON file.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = _parse_args(argv)

    sources = None
    if args.sources:
        with open(args.sources, encoding="utf-8") as fh:
            sources = json.load(fh)

    run(
        sources=sources,
        max_per_source=args.max_per_source,
        use_ai=args.use_ai,
        output_file=args.output,
        model=args.model,
    )


if __name__ == "__main__":
    main()
