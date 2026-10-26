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

REQUEST_PATTERNS = [
    "wie kent",
    "iemand die",
    "waar kan ik",
    "gezocht",
    "monteur gezocht",
    "garage gezocht",
    "auto kapot",
]

URGENT_PATTERNS = [
    "kapot",
    "storing",
    "pech",
    "vandaag",
    "snel",
    "dringend",
]


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    cleaned = value.lower()
    cleaned = cleaned.replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def contains_any(text: str, keywords: list[str]) -> list[str]:
    text_norm = normalize_text(text)
    matches: list[str] = []
    for keyword in keywords:
        if keyword.lower() in text_norm:
            matches.append(keyword)
    return matches


def is_dutch_like(text: str) -> bool:
    sample = normalize_text(text)
    dutch_tokens = {
        "ik",
        "de",
        "het",
        "een",
        "auto",
        "kapot",
        "garage",
        "monteur",
        "reparatie",
        "apk",
        "pech",
        "storing",
        "vandaag",
    }
    return sum(1 for token in dutch_tokens if token in sample) > 0


def location_match(text: str, cities: list[str]) -> str | None:
    sample = normalize_text(text)
    for city in cities:
        city_norm = normalize_text(city)
        if city_norm in sample:
            return city
    return None
