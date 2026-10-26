from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Any

from .models import Lead


class Storage:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TEXT,
                    detected_at TEXT NOT NULL,
                    language TEXT NOT NULL,
                    score INTEGER NOT NULL DEFAULT 0,
                    matched_keywords TEXT NOT NULL DEFAULT '[]',
                    location_hint TEXT,
                    status TEXT NOT NULL DEFAULT 'new'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_hashes (
                    hash TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO settings(key, value) VALUES ('retention_days', '30')"
            )

    def add_lead(self, lead: Lead) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO leads(
                    id, source, title, text, url, published_at, detected_at,
                    language, score, matched_keywords, location_hint, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lead.id,
                    lead.source,
                    lead.title,
                    lead.text,
                    lead.url,
                    lead.published_at.isoformat() if lead.published_at else None,
                    lead.detected_at.isoformat(),
                    lead.language,
                    lead.score,
                    json.dumps(lead.matched_keywords),
                    lead.location_hint,
                    lead.status,
                ),
            )

    def add_seen_hash(self, digest: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO seen_hashes(hash, created_at) VALUES (?, ?)",
                (digest, datetime.utcnow().isoformat()),
            )

    def has_seen_hash(self, digest: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM seen_hashes WHERE hash = ?", (digest,)).fetchone()
            return row is not None

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        return row["value"]

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def purge_retention(self, retention_days: int = 30) -> int:
        cutoff = (datetime.utcnow() - timedelta(days=retention_days)).isoformat()
        with self._connect() as conn:
            deleted_leads = conn.execute("DELETE FROM leads WHERE detected_at < ?", (cutoff,)).rowcount
            conn.execute("DELETE FROM seen_hashes WHERE created_at < ?", (cutoff,))
            return deleted_leads

    def list_leads(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM leads
                ORDER BY detected_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def hash_lead(source: str, title: str, url: str) -> str:
        raw = f"{source}|{title.strip()}|{url.strip()}".lower()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
