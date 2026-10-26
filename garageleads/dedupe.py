from __future__ import annotations

import hashlib


def compute_hash(source: str, title: str, url: str) -> str:
    normalized = f"{source}|{title.strip()}|{url.strip()}".lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_duplicate(storage, source: str, title: str, url: str) -> bool:
    digest = compute_hash(source, title, url)
    return storage.has_seen_hash(digest)
