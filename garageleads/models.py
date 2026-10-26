from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime


class Lead(BaseModel):
    id: str
    source: str
    title: str
    text: str
    url: str
    published_at: datetime | None = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "nl"
    score: int = 0
    matched_keywords: list[str] = Field(default_factory=list)
    location_hint: str | None = None
    status: str = "new"

    @property
    def is_high_intent(self) -> bool:
        return self.score >= 50
