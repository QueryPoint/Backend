"""Real cross-user authorization checks through public API endpoints."""
from __future__ import annotations

import pytest

from ._helpers import upload_pdf

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_user_cannot_read_or_delete_another_users_document(qa_users):
    owner = await qa_users()
    intruder = await qa_users()
    doc_id = await upload_pdf(owner["client"], "owner-secret.pdf", "qa-owner-secret-token")

    get_response = await intruder["client"].get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 403, get_response.text

    delete_response = await intruder["client"].delete(f"/api/v1/documents/{doc_id}")
    assert delete_response.status_code == 403, delete_response.text

    still_present = await owner["client"].get(f"/api/v1/documents/{doc_id}")
    assert still_present.status_code == 200, still_present.text
