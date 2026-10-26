from __future__ import annotations

from datetime import datetime

from .filters import normalize_text


def score_lead(
    text: str,
    title: str,
    *,
    cities: list[str] | None = None,
    include_keywords: list[str] | None = None,
    negative_keywords: list[str] | None = None,
    threshold: int = 50,
    published_at: datetime | None = None,
) -> tuple[int, list[str], str | None]:
    combined = f"{title} {text}"
    normalized = normalize_text(combined)
    include = include_keywords or []
    negative = negative_keywords or []
    cities = cities or []

    score = 0
    matched = []
    for kw in include:
        if kw.lower() in normalized:
            matched.append(kw)

    if any(pattern in normalized for pattern in ["wie kent", "iemand die", "waar kan ik", "gezocht"]):
        score += 30
    if any(pattern in normalized for pattern in ["kapot", "storing", "pech", "vandaag", "snel", "dringend"]):
        score += 25
    if location_match := next((city for city in cities if city.lower() in normalized), None):
        score += 20
    if published_at is not None:
        hours_old = (datetime.utcnow() - published_at).total_seconds() / 3600
        if hours_old < 24:
            score += 15
    if len(matched) > 1:
        score += 10
    negative_hits = [kw for kw in negative if kw.lower() in normalized]
    if negative_hits:
        score -= 20

    if any(item in normalized for item in ["ik", "auto", "garage", "monteur", "reparatie"]):
        score += 5

    return max(0, score), matched, location_match
