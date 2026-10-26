from __future__ import annotations

from datetime import datetime

import httpx

from ..filters import contains_any
from ..models import Lead


class ManualAdapter:
    def from_url(self, url: str, title: str | None = None, text: str | None = None) -> Lead:
        fetched_text = text or ""
        if not fetched_text and url.startswith("http"):
            try:
                with httpx.Client(timeout=20.0) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    fetched_text = response.text[:2000]
            except Exception:
                fetched_text = ""

        return Lead(
            id=f"manual:{url}",
            source="manual",
            title=title or "Manual lead",
            text=fetched_text,
            url=url,
            published_at=datetime.utcnow(),
            detected_at=datetime.utcnow(),
            language="nl",
            score=0,
            matched_keywords=contains_any(f"{title or 'Manual lead'} {fetched_text}", ["monteur", "garage", "reparatie", "apk", "kapot", "storing"]),
        )
