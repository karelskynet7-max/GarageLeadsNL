from __future__ import annotations

from datetime import datetime

import feedparser
import httpx

from ..filters import contains_any
from ..models import Lead


class RSSAdapter:
    def __init__(self, user_agent: str = "GarageLeadsNL/0.1 (monitoring only)"):
        self.user_agent = user_agent

    def fetch(self, urls: list[str] | None = None) -> list[Lead]:
        feed_urls = urls or [
            "https://news.google.com/rss/search?q=monteur+Nederland+auto+reparatie",
            "https://news.google.com/rss/search?q=garage+Nederland+auto+kapot",
        ]
        leads: list[Lead] = []
        for url in feed_urls:
            try:
                with httpx.Client(headers={"User-Agent": self.user_agent}, timeout=20.0) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    parsed = feedparser.parse(response.text)
            except Exception:
                continue

            for entry in parsed.entries:
                title = entry.get("title", "Untitled")
                text = entry.get("summary", title)
                link = entry.get("link", "")
                published = entry.get("published_parsed")
                dt = datetime(*published[:6]) if published else None
                leads.append(
                    Lead(
                        id=f"rss:{title}:{link}",
                        source="rss",
                        title=title,
                        text=text,
                        url=link,
                        published_at=dt,
                        detected_at=datetime.utcnow(),
                        language="nl",
                        score=0,
                        matched_keywords=contains_any(f"{title} {text}", ["monteur", "garage", "reparatie", "apk", "kapot", "storing"]),
                    )
                )
        return leads
