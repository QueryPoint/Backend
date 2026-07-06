"""Real flow: API upload -> S3 object -> PostgreSQL metadata -> Elasticsearch chunks."""
from __future__ import annotations

import pytest
from botocore.exceptions import ClientError

from ._helpers import eventually, es_user_doc_count, upload_pdf

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_upload_persists_object_metadata_and_search_chunks(qa_users, qa_pg, qa_s3, qa_es, qa_settings):
    user = await qa_users()
    token = "qa-upload-indexing-unique-token"
    doc_id = await upload_pdf(user["client"], "qa-upload.pdf", token)

    row = await qa_pg.fetchrow(
        "SELECT doc_name, doc_size, doc_type FROM documents WHERE doc_id = $1 AND user_id = $2",
        doc_id,
        user["user_id"],
    )
    assert row is not None
    assert row["doc_name"] == "qa-upload.pdf"
    assert row["doc_size"] > 0

    # This is the business contract. With the current backend it exposes BUG-DOC-001
    # if DocType values are accidentally tuples and produce `.('pdf',)` in the key.
    expected_key = f"{user['user_id']}/{doc_id}.pdf"
    try:
        qa_s3.head_object(Bucket=qa_settings.s3_bucket, Key=expected_key)
    except ClientError as error:
        pytest.fail(f"Expected S3 object key {expected_key!r} was not created: {error}")

    async def indexed() -> None:
        assert await es_user_doc_count(qa_es, qa_settings.es_index, user["user_id"], doc_id) >= 1

    await eventually(indexed)
