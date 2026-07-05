from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from .helpers import register_via_ui


@pytest.mark.e2e
def test_user_can_register_open_documents_and_log_out(e2e_page, e2e_base_url, e2e_credentials):
    """Critical browser path: registration → authenticated area → logout.

    This scenario is intentionally a real UI flow: no API request is used to
    create a cookie or to bypass the registration form.
    """
    register_via_ui(
        e2e_page,
        e2e_base_url,
        e2e_credentials.username,
        e2e_credentials.password,
    )

    expect(e2e_page.get_by_text(e2e_credentials.username, exact=True)).to_be_visible()
    e2e_page.get_by_role("button", name="Выйти").click()

    expect(e2e_page).to_have_url(re.compile(r".*/login$"))
    expect(e2e_page.get_by_role("button", name="Войти")).to_be_visible()
