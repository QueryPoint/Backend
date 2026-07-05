from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from .helpers import register_via_ui, upload_pdf_via_ui


def _copy_fixture_with_unique_name(tmp_path: Path, source: Path, suffix: str) -> tuple[Path, str]:
    name = f"e2e_{suffix}_{uuid4().hex[:8]}.pdf"
    target = tmp_path / name
    target.write_bytes(source.read_bytes())
    return target, name


@pytest.mark.e2e
def test_user_can_upload_document_and_see_it_in_documents_list(
    e2e_page,
    e2e_base_url,
    e2e_credentials,
    sample_pdf_path,
    tmp_path,
):
    register_via_ui(e2e_page, e2e_base_url, e2e_credentials.username, e2e_credentials.password)
    document_path, document_name = _copy_fixture_with_unique_name(tmp_path, sample_pdf_path, "upload")

    upload_pdf_via_ui(e2e_page, e2e_base_url, document_path, document_name)

    e2e_page.get_by_role("link", name="Документы").click()
    expect(e2e_page.get_by_text(document_name, exact=True)).to_be_visible()


@pytest.mark.e2e
def test_user_can_delete_document_from_documents_list(
    e2e_page,
    e2e_base_url,
    e2e_credentials,
    sample_pdf_path,
    tmp_path,
):
    register_via_ui(e2e_page, e2e_base_url, e2e_credentials.username, e2e_credentials.password)
    document_path, document_name = _copy_fixture_with_unique_name(tmp_path, sample_pdf_path, "delete")
    upload_pdf_via_ui(e2e_page, e2e_base_url, document_path, document_name)

    e2e_page.get_by_role("link", name="Документы").click()
    expect(e2e_page.get_by_text(document_name, exact=True)).to_be_visible()
    e2e_page.get_by_title("Удалить").click()
    expect(e2e_page.get_by_role("heading", name="Удалить документ?")).to_be_visible()
    e2e_page.get_by_role("button", name="Удалить", exact=True).last.click()

    expect(e2e_page.get_by_text(document_name, exact=True)).not_to_be_visible()
    expect(e2e_page.get_by_role("heading", name="Нет документов")).to_be_visible()
