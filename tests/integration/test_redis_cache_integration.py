"""Real Redis cache behavior for the search endpoint."""
from __future__ import annotations

import json

import pytest

from ._helpers import cache_key, upload_pdf

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_search_populates_and_reuses_real_redis_cache(qa_users, qa_redis):
    user = await qa_users()
    query = "qa-real-redis-cache-token"
    await upload_pdf(user["client"], "redis-cache.pdf", query)
    key = cache_key(user["user_id"], query)
    await qa_redis.delete(key)

    first = await user["client"].get("/api/v1/search", params={"q": query})
    assert first.status_code == 200, first.text
    cached_raw = await qa_redis.get(key)
    assert cached_raw is not None, "Search response was not written to Redis"
    assert json.loads(cached_raw) == first.json()
    ttl = await qa_redis.ttl(key)
    assert 0 < ttl <= 300

    # Seed a sentinel directly into the real Redis key. A second backend request
    # must return it, demonstrating cache hit rather than a second ES query.
    sentinel = [{"file_name": "cache-sentinel.pdf", "page_number": 1, "chunk_id": "qa", "text": "cached", "score": 1.0}]
    await qa_redis.set(key, json.dumps(sentinel), ex=30)
    second = await user["client"].get("/api/v1/search", params={"q": query})
    assert second.status_code == 200, second.text
    assert second.json() == sentinel
