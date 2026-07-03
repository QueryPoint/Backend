"""Real deletion flow across API, PostgreSQL, S3 and Elasticsearch."""
from __future__ import annotations

import pytest
from botocore.exceptions import ClientError

from ._helpers import eventually, es_user_doc_count, upload_pdf

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_delete_removes_metadata_s3_object_and_index_chunks(qa_users, qa_pg, qa_s3, qa_es, qa_settings):
    user = await qa_users()
    doc_id = await upload_pdf(user["client"], "delete-real.pdf", "qa-delete-flow-token")

    # Find actual test object so cleanup/verification remains meaningful even when
    # a filename bug exists; the upload contract itself checks canonical extension.
    objects = qa_s3.list_objects_v2(Bucket=qa_settings.s3_bucket, Prefix=f"{user['user_id']}/{doc_id}")
    keys = [entry["Key"] for entry in objects.get("Contents", [])]
    assert len(keys) == 1, f"Expected exactly one S3 object for document, got {keys!r}"
    object_key = keys[0]

    deleted = await user["client"].delete(f"/api/v1/documents/{doc_id}")
    assert deleted.status_code == 204, deleted.text

    async def db_deleted() -> None:
        assert await qa_pg.fetchval("SELECT 1 FROM documents WHERE doc_id = $1", doc_id) is None

    async def es_deleted() -> None:
        assert await es_user_doc_count(qa_es, qa_settings.es_index, user["user_id"], doc_id) == 0

    await eventually(db_deleted)
    await eventually(es_deleted)
    with pytest.raises(ClientError):
        qa_s3.head_object(Bucket=qa_settings.s3_bucket, Key=object_key)
