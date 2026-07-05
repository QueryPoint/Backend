"""Common fixtures for browser E2E tests.

The tests are deliberately opt-in. They call a live frontend in a live QA
environment and must never run against production by accident.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import Page


E2E_ROOT = Path(__file__).resolve().parent
DEFAULT_FRONTEND_URL = "http://127.0.0.1:5173"


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


def _required_e2e_url() -> str:
    value = os.getenv("E2E_BASE_URL", DEFAULT_FRONTEND_URL).rstrip("/")
    if not value.startswith(("http://", "https://")):
        pytest.fail("E2E_BASE_URL must start with http:// or https://")
    return value


@pytest.fixture(autouse=True)
def require_e2e_environment() -> None:
    """Protect normal unit/API runs from silently opening a browser."""
    if os.getenv("QA_E2E") != "1":
        pytest.skip("E2E tests are disabled; set QA_E2E=1 and start the frontend")


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    return _required_e2e_url()


@pytest.fixture
def e2e_page(page: Page) -> Page:
    """A fresh browser page provided by pytest-playwright for each test."""
    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(30_000)
    return page


@pytest.fixture
def e2e_credentials() -> Credentials:
    """Unique, backend-valid credentials; the backend allows max 25 username chars."""
    return Credentials(
        username=f"e2e{uuid4().hex[:16]}",
        password="E2E_password_123",
    )


@pytest.fixture
def sample_pdf_path() -> Path:
    return E2E_ROOT / "fixtures" / "e2e-searchable.pdf"
