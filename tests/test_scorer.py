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
