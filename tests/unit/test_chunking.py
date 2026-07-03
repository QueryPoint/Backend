
from src.core.elasticsearch.es_servise import ElasticService

def test_chunking_empty_text():
    assert ElasticService._chunk_text("") == []

def test_chunking_short_text_is_one_chunk():
    assert ElasticService._chunk_text("hello") == ["hello"]

def test_chunking_uses_overlap():
    text = "a"*1100
    chunks = ElasticService._chunk_text(text, size=1000, overlap=100)
    assert len(chunks) == 2
    assert chunks[0] == "a"*1000
    assert chunks[1] == "a"*200

def test_chunking_strips_whitespace_and_skips_empty():
    assert ElasticService._chunk_text("   hello   ", size=1000, overlap=100) == ["hello"]
