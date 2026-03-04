"""
AI summarizer – uses the OpenAI Chat API to summarize news articles.
"""

from __future__ import annotations

import logging
import os
import re
from typing import List

from openai import OpenAI

from .news_fetcher import NewsItem

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an AI news analyst. Given a list of AI news article titles and summaries, "
    "provide a concise one-sentence insight for each article that highlights the key takeaway "
    "for someone following developments in artificial intelligence. "
    "Reply with one insight per line, in the same order as the input articles."
)


def _build_user_message(items: List[NewsItem]) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        text = item.summary or item.title
        lines.append(f"{i}. [{item.source}] {item.title}: {text[:300]}")
    return "\n".join(lines)


def summarize_news(
    items: List[NewsItem],
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
    batch_size: int = 10,
) -> List[NewsItem]:
    """Enrich each :class:`NewsItem` with an AI-generated one-sentence summary.

    Calls are batched so that large lists don't exceed context limits.

    Args:
        items: News items to summarize.
        api_key: OpenAI API key.  Falls back to the ``OPENAI_API_KEY``
                 environment variable.
        model: OpenAI model to use.
        batch_size: Number of articles per API call.

    Returns:
        The same list of items, each with :attr:`~NewsItem.ai_summary` set.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        logger.warning("No OpenAI API key found; skipping AI summarization.")
        return items

    client = OpenAI(api_key=key)

    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        user_msg = _build_user_message(batch)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.3,
            )
            raw = response.choices[0].message.content or ""
            lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
            for i, item in enumerate(batch):
                if i < len(lines):
                    # Strip leading numbering like "1. " if present
                    # Strip leading numbering like "1. " or "12. " if present
                    insight = re.sub(r"^\d+\.\s*", "", lines[i])
                    item.ai_summary = insight
        except Exception as exc:  # pragma: no cover
            logger.error("OpenAI API call failed for batch starting at %d: %s", start, exc)

    return items
