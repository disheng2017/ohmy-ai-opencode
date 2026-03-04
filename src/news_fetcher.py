"""
News fetcher module – retrieves AI news items from RSS feeds.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import feedparser

logger = logging.getLogger(__name__)

# Curated list of AI-related RSS feeds
DEFAULT_SOURCES: List[dict] = [
    {
        "name": "MIT Technology Review – AI",
        "url": "https://www.technologyreview.com/feed/",
    },
    {
        "name": "The Verge – AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "VentureBeat – AI",
        "url": "https://venturebeat.com/category/ai/feed/",
    },
    {
        "name": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
    },
    {
        "name": "Hacker News – AI",
        "url": "https://hnrss.org/newest?q=AI+LLM+machine+learning&points=50",
    },
]


@dataclass
class NewsItem:
    """A single news article."""

    title: str
    url: str
    source: str
    summary: str = ""
    published: str = ""
    ai_summary: str = ""

    def __str__(self) -> str:
        lines = [
            f"[{self.source}] {self.title}",
            f"  URL: {self.url}",
        ]
        if self.published:
            lines.append(f"  Published: {self.published}")
        if self.ai_summary:
            lines.append(f"  AI Summary: {self.ai_summary}")
        elif self.summary:
            lines.append(f"  Summary: {self.summary[:200]}...")
        return "\n".join(lines)


def fetch_news(sources: List[dict] | None = None, max_per_source: int = 5) -> List[NewsItem]:
    """Fetch news articles from the given RSS feed sources.

    Args:
        sources: List of dicts with ``name`` and ``url`` keys.
                 Defaults to :data:`DEFAULT_SOURCES`.
        max_per_source: Maximum number of articles to retrieve per source.

    Returns:
        A flat list of :class:`NewsItem` objects.
    """
    if sources is None:
        sources = DEFAULT_SOURCES

    items: List[NewsItem] = []
    for source in sources:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:max_per_source]:
                summary = getattr(entry, "summary", "") or ""
                # Strip HTML tags from summary
                summary = re.sub(r"<[^>]+>", "", summary).strip()

                published = ""
                if hasattr(entry, "published"):
                    published = entry.published
                elif hasattr(entry, "updated"):
                    published = entry.updated

                items.append(
                    NewsItem(
                        title=entry.get("title", "").strip(),
                        url=entry.get("link", ""),
                        source=source["name"],
                        summary=summary,
                        published=published,
                    )
                )
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to fetch feed %s: %s", source["url"], exc)

    logger.info("Fetched %d news items from %d sources.", len(items), len(sources))
    return items
