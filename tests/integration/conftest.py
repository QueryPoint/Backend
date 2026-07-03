"""Guard and fixtures for real end-to-end integration tests.

These tests NEVER mock PostgreSQL, Redis, Elasticsearch, S3/MinIO, RabbitMQ,
or the backend HTTP/WebSocket application. They run only after an explicit
opt-in so an ordinary local pytest run cannot write into a non-test service.

The fixture functions live in ``_helpers.py`` to keep shared test helpers in
one place. They are imported here so pytest registers them for every module in
``tests/integration``.
"""
from __future__ import annotations

import os

import pytest

# Re-export fixtures from the helper module.  pytest discovers fixtures from
# conftest.py; without these imports qa_users/qa_pg/qa_s3/... are not visible
# to integration test modules.
from ._helpers import (  # noqa: F401
    qa_es,
    qa_http,
    qa_pg,
    qa_redis,
    qa_s3,
    qa_settings,
    qa_users,
)


@pytest.fixture(autouse=True)
def require_real_infrastructure() -> None:
    if os.getenv("QA_REAL_INTEGRATION") != "1":
        pytest.skip(
            "real integration tests are disabled; set QA_REAL_INTEGRATION=1 "
            "and provide QA_* test-environment variables"
        )
