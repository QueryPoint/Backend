from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
def test_anonymous_user_is_redirected_to_login(e2e_page, e2e_base_url):
    e2e_page.goto(f"{e2e_base_url}/documents", wait_until="domcontentloaded")

    expect(e2e_page).to_have_url(re.compile(r".*/login$"))
    expect(e2e_page.get_by_role("heading", name="База знаний")).to_be_visible()
    expect(e2e_page.get_by_role("button", name="Войти")).to_be_visible()


@pytest.mark.e2e
def test_registration_blocks_username_with_forbidden_characters(e2e_page, e2e_base_url):
    e2e_page.goto(f"{e2e_base_url}/register", wait_until="domcontentloaded")

    e2e_page.get_by_placeholder("student_2026").fill("bad-name")

    expect(e2e_page.get_by_text("Только латиница, цифры и _", exact=True)).to_be_visible()
    expect(e2e_page.get_by_role("button", name="Создать аккаунт")).to_be_disabled()


@pytest.mark.e2e
def test_registration_blocks_mismatched_passwords(e2e_page, e2e_base_url):
    e2e_page.goto(f"{e2e_base_url}/register", wait_until="domcontentloaded")

    e2e_page.get_by_placeholder("student_2026").fill("e2e_valid_user")
    e2e_page.get_by_placeholder("Введите пароль").fill("Password_123")
    e2e_page.get_by_placeholder("Повторите пароль").fill("Password_456")

    expect(e2e_page.get_by_text("Пароли не совпадают", exact=True)).to_be_visible()
    expect(e2e_page.get_by_role("button", name="Создать аккаунт")).to_be_disabled()


@pytest.mark.e2e
def test_login_blocks_invalid_username_before_submit(e2e_page, e2e_base_url):
    e2e_page.goto(f"{e2e_base_url}/login", wait_until="domcontentloaded")

    e2e_page.get_by_placeholder("student_2026").fill("wrong-name")
    e2e_page.get_by_placeholder("Введите пароль").fill("Password_123")

    expect(e2e_page.get_by_text("Только латиница, цифры и _", exact=True)).to_be_visible()
    expect(e2e_page.get_by_role("button", name="Войти")).to_be_disabled()
