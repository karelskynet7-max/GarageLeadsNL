from __future__ import annotations

from dataclasses import dataclass

from .dedupe import compute_hash
from .storage import Storage


@dataclass
class LeadPipeline:
    storage: Storage
    keywords: list[str]
    negative_keywords: list[str]
    cities: list[str]
    threshold: int = 50

    def process(self, lead):
        from .scorer import score_lead

        score, matched, location = score_lead(
            lead.text,
            lead.title,
            cities=self.cities,
            include_keywords=self.keywords,
            negative_keywords=self.negative_keywords,
            threshold=self.threshold,
            published_at=lead.published_at,
        )

        lead.score = score
        lead.matched_keywords = matched
        lead.location_hint = location

        if score < self.threshold:
            return None

        digest = compute_hash(lead.source, lead.title, lead.url)
        if self.storage.has_seen_hash(digest):
            return None

        lead.id = digest
        self.storage.add_seen_hash(digest)
        self.storage.add_lead(lead)
        return lead
