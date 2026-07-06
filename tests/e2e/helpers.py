"""UI actions shared by E2E scenarios.

Selectors use visible user-facing text and placeholders because the current
frontend does not yet expose stable data-testid attributes.
"""
from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, expect


def open_register(page: Page, base_url: str) -> None:
    response = page.goto(f"{base_url}/register", wait_until="domcontentloaded")
    assert response is not None and response.ok, "The frontend did not serve /register"
    expect(page.get_by_role("heading", name="Интеллектуальная база знаний")).to_be_visible()


def register_via_ui(page: Page, base_url: str, username: str, password: str) -> None:
    open_register(page, base_url)
    page.get_by_placeholder("student_2026").fill(username)
    page.get_by_placeholder("Введите пароль").fill(password)
    page.get_by_placeholder("Повторите пароль").fill(password)
    page.get_by_role("button", name="Создать аккаунт").click()
    page.wait_for_url(re.compile(r".*/documents$"))
    expect(page.get_by_role("heading", name="Документы")).to_be_visible()


def upload_pdf_via_ui(page: Page, base_url: str, pdf_path: Path, visible_name: str) -> None:
    page.goto(f"{base_url}/upload", wait_until="domcontentloaded")
    expect(page.get_by_role("heading", name="Загрузка документов")).to_be_visible()
    page.locator("input[type=file]").set_input_files(str(pdf_path))
    expect(page.get_by_text(visible_name, exact=True)).to_be_visible()
    expect(page.get_by_text("Загружен", exact=True)).to_be_visible()
