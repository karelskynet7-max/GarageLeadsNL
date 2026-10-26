from __future__ import annotations

import re

DUTCH_INCLUDE_KEYWORDS = [
    "monteur",
    "garage",
    "reparatie",
    "apk",
    "storing",
    "kapot",
    "pech",
    "onderhoud",
    "remmen",
    "motor",
    "versnellingsbak",
    "koppeling",
    "uitlaat",
    "accu",
    "banden",
    "olie",
    "koelvloeistof",
    "start niet",
    "check engine",
    "schade",
    "slepen",
]

DUTCH_NEGATIVE_KEYWORDS = [
    "vacature",
    "sollicitatie",
    "verkoop",
    "te koop",
    "gevonden",
    "vermist",
    "hoeveel kost",
]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def contains_any(text: str, keywords: list[str]) -> list[str]:
    text_norm = normalize_text(text)
    return [kw for kw in keywords if kw.lower() in text_norm]


def is_dutch_like(text: str) -> bool:
    sample = normalize_text(text)
    dutch_tokens = {"ik", "de", "het", "een", "auto", "kapot", "garage", "monteur", "reparatie", "apk", "pech", "storing", "vandaag"}
    return sum(1 for token in dutch_tokens if token in sample) > 0


def location_match(text: str, cities: list[str]) -> str | None:
    sample = normalize_text(text)
    for city in cities:
        city_norm = city.lower()
        if city_norm in sample:
            return city
    return None
