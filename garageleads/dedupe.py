from __future__ import annotations

import hashlib


def compute_hash(source: str, title: str, url: str) -> str:
    raw = f"{source}|{title.strip()}|{url.strip()}".lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
