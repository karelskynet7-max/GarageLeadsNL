from __future__ import annotations

from datetime import datetime

from .filters import (
    DUTCH_INCLUDE_KEYWORDS,
    DUTCH_NEGATIVE_KEYWORDS,
    REQUEST_PATTERNS,
    URGENT_PATTERNS,
    contains_any,
    is_dutch_like,
    location_match,
    normalize_text,
)


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
    include = include_keywords or DUTCH_INCLUDE_KEYWORDS
    negative = negative_keywords or DUTCH_NEGATIVE_KEYWORDS
    active_cities = cities or []

    score = 0
    matched = contains_any(normalized, include)
    negative_hits = contains_any(normalized, negative)

    if any(pattern in normalized for pattern in [
        "wie kent",
        "iemand die",
        "waar kan ik",
        "gezocht",
        "monteur gezocht",
        "garage gezocht",
        "auto kapot",
    ]):
        score += 30

    if any(pattern in normalized for pattern in [
        "kapot",
        "storing",
        "pech",
        "vandaag",
        "snel",
        "dringend",
    ]):
        score += 25

    city_hint = location_match(normalized, active_cities)
    if city_hint:
        score += 20

    if published_at is not None:
        age_hours = (datetime.utcnow() - published_at).total_seconds() / 3600
        if age_hours < 24:
            score += 15

    if len(matched) >= 2:
        score += 10

    if negative_hits:
        score -= 20

    if is_dutch_like(normalized):
        score += 5

    score = max(0, score)
    return score, matched, city_hint
