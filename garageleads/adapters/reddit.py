from __future__ import annotations

from datetime import datetime
import time

import httpx

from ..filters import contains_any
from ..models import Lead


class RedditAdapter:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None, user_agent: str = "GarageLeadsNL/0.1"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

    def _headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.user_agent}
        if self.client_id and self.client_secret:
            import base64

            token = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        return headers

    def fetch(self, query_terms: list[str] | None = None, polite_delay_seconds: float = 1.2) -> list[Lead]:
        terms = query_terms or ["monteur gezocht", "auto kapot", "garage aanrader", "APK", "reparatie"]
        leads: list[Lead] = []
        for term in terms:
            time.sleep(polite_delay_seconds)
            url = "https://www.reddit.com/search.json"
            params = {"q": term, "restrict_sr": "on", "sort": "new", "limit": 10}
            try:
                with httpx.Client(headers=self._headers(), timeout=20.0) as client:
                    response = client.get(url, params=params)
                    response.raise_for_status()
                    payload = response.json()
            except Exception:
                continue

            for item in payload.get("data", {}).get("children", []):
                data = item.get("data", {})
                title = data.get("title", "Untitled")
                text = data.get("selftext", "") or title
                link = data.get("url") or f"https://www.reddit.com{data.get('permalink', '')}"
                leads.append(
                    Lead(
                        id=f"reddit:{data.get('id', title)}",
                        source="reddit",
                        title=title,
                        text=text,
                        url=link,
                        published_at=datetime.utcfromtimestamp(data.get("created_utc", 0)),
                        detected_at=datetime.utcnow(),
                        language="nl",
                        score=0,
                        matched_keywords=contains_any(f"{title} {text}", ["monteur", "garage", "apk", "reparatie", "kapot", "storing"]),
                    )
                )
        return leads
