from __future__ import annotations

import json
from datetime import datetime

import httpx

from .storage import Storage


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, storage: Storage | None = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.storage = storage
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send(
        self,
        title: str,
        score: int,
        matched_keywords: list[str],
        location_hint: str | None,
        url: str,
    ) -> dict:
        if not self.bot_token or not self.chat_id:
            return {"ok": False, "reason": "missing credentials"}

        text = (
            "*Nieuwe lead*\n"
            f"Titel: {title}\n"
            f"Score: {score}\n"
            f"Keywords: {', '.join(matched_keywords) if matched_keywords else 'n.v.t.'}\n"
            f"Locatie: {location_hint or 'onbekend'}\n"
            f"URL: {url}"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "Open link", "url": url}],
                    [{"text": "Mark handled", "callback_data": "mark_handled"}],
                ]
            },
        }

        with httpx.Client(timeout=20.0) as client:
            return client.post(f"{self.base_url}/sendMessage", json=payload).json()
