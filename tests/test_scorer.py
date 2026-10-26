from __future__ import annotations

from datetime import datetime, timedelta

from garageleads.scorer import score_lead


def test_score_request_and_urgency():
    score, matched, location = score_lead(
        "Wie kent iemand die mijn auto snel repareert? Auto kapot in Rotterdam.",
        "Monteur gezocht",
        cities=["Rotterdam"],
        include_keywords=["monteur", "garage", "reparatie", "kapot", "storing"],
        negative_keywords=["vacature", "verkoop"],
        published_at=datetime.utcnow() - timedelta(hours=2),
    )
    assert score >= 50
    assert location == "Rotterdam"


def test_score_rejects_old_posts():
    score, matched, location = score_lead(
        "Ik heb auto kapot in Rotterdam.",
        "Garage gezocht",
        cities=["Rotterdam"],
        include_keywords=["garage", "kapot"],
        negative_keywords=[],
        published_at=datetime.utcnow() - timedelta(days=20),
        freshness_days=14,
    )
    assert score == 0
    assert matched == []
    assert location is None
