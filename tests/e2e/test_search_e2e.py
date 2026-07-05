from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from .helpers import register_via_ui, upload_pdf_via_ui


@pytest.mark.e2e
def test_search_finds_uploaded_document_for_its_owner(
    e2e_page,
    e2e_base_url,
    e2e_credentials,
    sample_pdf_path,
    tmp_path,
):
    """E2E path: browser upload → backend indexing → browser search results."""
    register_via_ui(e2e_page, e2e_base_url, e2e_credentials.username, e2e_credentials.password)

    document_name = f"e2e_search_{uuid4().hex[:8]}.pdf"
    document_path = tmp_path / document_name
    document_path.write_bytes(sample_pdf_path.read_bytes())
    upload_pdf_via_ui(e2e_page, e2e_base_url, document_path, document_name)

    e2e_page.get_by_role("link", name="Поиск").click()
    query = "PLAYWRIGHT_E2E_SEARCH_TOKEN"
    e2e_page.get_by_placeholder("Введите поисковый запрос...").fill(query)
    e2e_page.get_by_role("button", name="Найти").click()

    expect(e2e_page.get_by_text(document_name, exact=True)).to_be_visible(timeout=30_000)
    expect(e2e_page.get_by_text(query, exact=False)).to_be_visible(timeout=30_000)
