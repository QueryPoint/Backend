"""Guard for health checks that require live external services."""
from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def require_health_environment() -> None:
    if os.getenv("QA_HEALTH") != "1":
        pytest.skip("health checks are disabled; set QA_HEALTH=1 and provide QA_* endpoints")
