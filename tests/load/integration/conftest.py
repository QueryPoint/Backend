"""Reuse real integration fixtures for load/integration smoke scenarios."""
from __future__ import annotations

from tests.integration.conftest import require_real_infrastructure  # noqa: F401
from tests.integration._helpers import (  # noqa: F401
    qa_es,
    qa_http,
    qa_pg,
    qa_redis,
    qa_s3,
    qa_settings,
    qa_users,
)
