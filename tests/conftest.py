"""Общий bootstrap и фикстуры QA-набора.

Этот файл намеренно выполняет настройку ДО импорта модулей backend из тестов.
Backend не меняется: тесты подменяют только внешние зависимости во время test run.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# python-magic on Windows needs native libmagic.dll.  Unit/API tests do not need
# a real native detector, therefore provide a tiny test-only stub before
# DocumentService is imported by collected tests.
magic_stub = types.ModuleType("magic")
magic_stub.from_buffer = lambda _content, mime=True: "application/octet-stream"
sys.modules["magic"] = magic_stub


import os
import sys
import types
from pathlib import Path
from urllib.parse import urlparse
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.toml"


def set_env_if_missing(name: str, value: object | None) -> None:
    """
    Устанавливает QA-переменную только если:
    1. она ещё не задана вручную;
    2. значение действительно существует.
    """
    if not os.getenv(name) and value not in (None, ""):
        os.environ[name] = str(value)


def load_qa_environment_from_config() -> None:
    """
    Читает config.toml backend-проекта и формирует QA_* переменные.

    QA_* имеет приоритет:
    если переменная уже задана вручную, значение config.toml не перезаписывается.
    """
    if not CONFIG_PATH.exists():
        return

    with CONFIG_PATH.open("rb") as file:
        config = tomllib.load(file)

    database = config.get("database", {})
    redis = config.get("redis", {})
    elasticsearch = config.get("elasticsearch", {})
    rabbitmq = config.get("rabbitmq", {})
    s3 = config.get("s3", {})

    # PostgreSQL
    set_env_if_missing("QA_POSTGRES_HOST", database.get("postgres_host"))
    set_env_if_missing("QA_POSTGRES_PORT", database.get("postgres_port"))
    set_env_if_missing("QA_POSTGRES_USERNAME", database.get("postgres_username"))
    set_env_if_missing("QA_POSTGRES_PASSWORD", database.get("postgres_password"))
    set_env_if_missing("QA_POSTGRES_DB", database.get("postgres_db"))

    # Redis
    set_env_if_missing("QA_REDIS_HOST", redis.get("HOST"))
    set_env_if_missing("QA_REDIS_PORT", redis.get("PORT"))
    set_env_if_missing("QA_REDIS_PASSWORD", redis.get("PASSWORD"))

    # Elasticsearch
    elasticsearch_url = elasticsearch.get("URL")
    set_env_if_missing("QA_ELASTICSEARCH_URL", elasticsearch_url)

    # RabbitMQ
    set_env_if_missing("QA_RABBITMQ_HOST", rabbitmq.get("HOST"))
    set_env_if_missing("QA_RABBITMQ_PORT", rabbitmq.get("PORT"))
    set_env_if_missing("QA_RABBITMQ_USER", rabbitmq.get("USER"))
    set_env_if_missing("QA_RABBITMQ_PASSWORD", rabbitmq.get("PASSWORD"))

    # S3 / MinIO
    s3_url = s3.get("ENDPOINT_URL")
    set_env_if_missing("QA_S3_ENDPOINT", s3_url)
    set_env_if_missing("QA_S3_ACCESS_KEY", s3.get("ACCESS_KEY_ID"))
    set_env_if_missing("QA_S3_SECRET_KEY", s3.get("ACCESS_SECRET_KEY"))
    set_env_if_missing("QA_S3_BUCKET", s3.get("BUCKET_NAME"))

    if s3_url:
        parsed_s3_url = urlparse(s3_url)
        set_env_if_missing("QA_S3_HOST", parsed_s3_url.hostname)
        set_env_if_missing(
            "QA_S3_PORT",
            parsed_s3_url.port or (443 if parsed_s3_url.scheme == "https" else 80),
        )

    # URL backend не хранится в config.toml, поэтому задаётся отдельно.
    set_env_if_missing("QA_BACKEND_URL", "http://localhost:8000")


load_qa_environment_from_config()


# -------------------------------------------------------------------
# Дальше остаётся уже существующий bootstrap для тестов.
# Он нужен для Windows, где python-magic часто не находит libmagic.dll.
# -------------------------------------------------------------------

if "magic" not in sys.modules:
    magic_module = types.ModuleType("magic")

    def from_buffer(_content: bytes, mime: bool = True) -> str:
        return "application/octet-stream"

    magic_module.from_buffer = from_buffer
    sys.modules["magic"] = magic_module


# Безопасные test-only значения для импортов backend-модулей.
# Не перезаписывают реальные значения из config.toml или QA_*.
set_env_if_missing("TESTING", "1")
set_env_if_missing("ELASTICSEARCH_URL", "http://127.0.0.1:9200")

# The backend reads config.toml at import time.  The local developer machine may
# not have a populated config.toml, while Elasticsearch/SQLAlchemy clients are
# constructed during module imports.  Populate safe syntactically-valid test
# values before importing any backend router/service.
from src.config.config import config

config.database.postgres_username = "qa_user"
config.database.postgres_password = "qa_password"
config.database.postgres_host = "127.0.0.1"
config.database.postgres_port = 5432
config.database.postgres_db = "qa_test_db"
config.database.alembic_postgres_host = "127.0.0.1"

config.elasticsearch.URL = "http://127.0.0.1:9200"
config.redis.HOST = "127.0.0.1"
config.redis.PORT = 6379
config.redis.PASSWORD = ""
config.rabbitmq.HOST = "127.0.0.1"
config.rabbitmq.PORT = 5672
config.rabbitmq.USER = "guest"
config.rabbitmq.PASSWORD = "guest"

config.s3.ENDPOINT_URL = "http://127.0.0.1:9000"
config.s3.ACCESS_KEY_ID = "qa-access-key"
config.s3.ACCESS_SECRET_KEY = "qa-secret-key"
config.s3.BUCKET_NAME = "qa-test-bucket"
config.s3.REGION = "us-east-1"

config.jwt.SECRET_KEY = "qa-test-secret"
config.jwt.ALGORITHM = "HS256"
config.jwt.ACCESS_TOKEN_EXPIRE_MINUTES = 15
config.jwt.REFRESH_TOKEN_EXPIRE_DAYS = 7


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def other_user_id():
    return uuid4()


@pytest.fixture
def fake_uow():
    """Минимальный UoW с асинхронными репозиториями для unit/API тестов."""
    return SimpleNamespace(
        user=SimpleNamespace(
            get_by_username=AsyncMock(),
            create=AsyncMock(),
            get_password_hash=AsyncMock(),
            get_by_id=AsyncMock(),
        ),
        document=SimpleNamespace(
            create=AsyncMock(),
            list=AsyncMock(),
            get_by_id=AsyncMock(),
            delete=AsyncMock(),
        ),
        search_history=SimpleNamespace(
            create=AsyncMock(),
            delete_by_user=AsyncMock(),
        ),
    )


@pytest.fixture
def fake_redis():
    client = MagicMock()
    client.set = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.delete = AsyncMock()
    client.exists = AsyncMock(return_value=0)
    return client


@pytest.fixture
def fake_es_client():
    client = MagicMock()
    client.index = AsyncMock()
    client.search = AsyncMock(return_value={"hits": {"hits": []}})
    client.delete_by_query = AsyncMock()
    client.indices = MagicMock()
    client.indices.exists = AsyncMock(return_value=True)
    client.indices.create = AsyncMock()
    client.indices.refresh = AsyncMock()
    return client
