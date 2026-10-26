from garageleads.dedupe import compute_hash
from garageleads.storage import Storage


def test_hash_consistency():
    hash_a = compute_hash("reddit", "Monteur gezocht", "https://example.com/1")
    hash_b = compute_hash("reddit", "Monteur gezocht", "https://example.com/1")
    assert hash_a == hash_b


def test_storage_hashes(tmp_path):
    db = tmp_path / "test.db"
    storage = Storage(db)
    digest = compute_hash("rss", "Kapotte auto", "https://example.com/lead")
    storage.add_seen_hash(digest)
    assert storage.has_seen_hash(digest) is True
