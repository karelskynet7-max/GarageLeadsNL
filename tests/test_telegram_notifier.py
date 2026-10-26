from garageleads.notifier import TelegramNotifier
from garageleads.storage import Storage


def test_telegram_notifier_builds_payload(monkeypatch, tmp_path):
    db = tmp_path / "lead.db"
    storage = Storage(db)

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json):
            class Response:
                def json(self):
                    return {"ok": True, "result": {"message_id": 1}}

            return Response()

    monkeypatch.setattr("garageleads.notifier.httpx.Client", DummyClient)
    notifier = TelegramNotifier("token", "12345", storage)
    result = notifier.send("Monteur gezocht", 80, ["monteur"], "Rotterdam", "https://example.com/lead")
    assert result["ok"] is True
