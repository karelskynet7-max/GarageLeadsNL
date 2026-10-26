from garageleads.adapters.rss import RSSAdapter


def test_rss_adapter_with_fixture(monkeypatch):
    sample_xml = """
    <rss version="2.0">
      <channel>
        <title>Garage News</title>
        <item>
          <title>Monteur gezocht in Utrecht</title>
          <link>https://example.com/lead</link>
          <description>Mijn auto is kapot en ik wil snel reparatie.</description>
          <pubDate>Mon, 22 Oct 2024 10:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, *args, **kwargs):
            class Response:
                text = sample_xml

                def raise_for_status(self):
                    return None

            return Response()

    monkeypatch.setattr("garageleads.adapters.rss.httpx.Client", DummyClient)
    adapter = RSSAdapter()
    leads = adapter.fetch(["https://example.com/rss"])
    assert len(leads) >= 1
    assert leads[0].source == "rss"
