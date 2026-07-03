"""Real search integration against the backend, PostgreSQL and Elasticsearch."""
from __future__ import annotations

import pytest

from ._helpers import eventually, es_user_doc_count, upload_pdf

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_search_returns_only_owner_documents(qa_users, qa_es, qa_settings):
    owner = await qa_users()
    other = await qa_users()
    shared_query = "qa-isolation-search-token"
    owner_doc = await upload_pdf(owner["client"], "owner-private.pdf", shared_query)
    other_doc = await upload_pdf(other["client"], "other-private.pdf", shared_query)

    async def indexed() -> None:
        assert await es_user_doc_count(qa_es, qa_settings.es_index, owner["user_id"], owner_doc) >= 1
        assert await es_user_doc_count(qa_es, qa_settings.es_index, other["user_id"], other_doc) >= 1

    await eventually(indexed)

    owner_response = await owner["client"].get("/api/v1/search", params={"q": shared_query})
    assert owner_response.status_code == 200, owner_response.text
    owner_names = {entry["file_name"] for entry in owner_response.json()}
    assert "owner-private.pdf" in owner_names
    assert "other-private.pdf" not in owner_names

    other_response = await other["client"].get("/api/v1/search", params={"q": shared_query})
    assert other_response.status_code == 200, other_response.text
    other_names = {entry["file_name"] for entry in other_response.json()}
    assert "other-private.pdf" in other_names
    assert "owner-private.pdf" not in other_names
