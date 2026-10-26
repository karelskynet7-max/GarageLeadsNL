from __future__ import annotations

import time
from datetime import datetime

import httpx


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, storage=None, *, rate_limit_seconds: int = 30):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.storage = storage
        self.rate_limit_seconds = rate_limit_seconds
        self._last_sent_at: datetime | None = None
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def should_send(self) -> bool:
        if self._last_sent_at is None:
            return True
        return (datetime.utcnow() - self._last_sent_at).total_seconds() >= self.rate_limit_seconds

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

        if not self.should_send():
            return {"ok": False, "reason": "rate_limited"}

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
            response = client.post(f"{self.base_url}/sendMessage", json=payload)
            result = response.json()
        if result.get("ok"):
            self._last_sent_at = datetime.utcnow()
        return result
