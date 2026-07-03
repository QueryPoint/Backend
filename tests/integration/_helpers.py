"""Shared utilities for real infrastructure integration tests.

No production defaults are used here.  Every endpoint/credential must be
explicitly passed through QA_* variables, and the tests clean only the unique
objects/users they create.
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from urllib.parse import urlparse
from uuid import UUID, uuid4

import asyncpg
import boto3
import httpx
import pytest
import redis.asyncio as redis
from botocore.config import Config
from botocore.exceptions import ClientError
from elasticsearch import AsyncElasticsearch


QA_PREFIX = "qait_"
PASSWORD = "QaPassword_123456"


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"{name} is not configured for the real QA environment")
    return value


@dataclass(frozen=True)
class QASettings:
    backend_url: str
    postgres_dsn: str
    redis_url: str
    elasticsearch_url: str
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    rabbitmq_url: str
    es_index: str

    @classmethod
    def from_env(cls) -> "QASettings":
        postgres_dsn = os.getenv("QA_POSTGRES_DSN")
        if not postgres_dsn:
            host = _required("QA_POSTGRES_HOST")
            port = os.getenv("QA_POSTGRES_PORT", "5432")
            user = _required("QA_POSTGRES_USERNAME")
            password = _required("QA_POSTGRES_PASSWORD")
            database = _required("QA_POSTGRES_DB")
            postgres_dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        redis_url = os.getenv("QA_REDIS_URL")
        if not redis_url:
            host = _required("QA_REDIS_HOST")
            port = os.getenv("QA_REDIS_PORT", "6379")
            password = os.getenv("QA_REDIS_PASSWORD", "")
            auth = f":{password}@" if password else ""
            redis_url = f"redis://{auth}{host}:{port}/0"

        rabbitmq_url = os.getenv("QA_RABBITMQ_URL")
        if not rabbitmq_url:
            host = _required("QA_RABBITMQ_HOST")
            port = os.getenv("QA_RABBITMQ_PORT", "5672")
            user = _required("QA_RABBITMQ_USER")
            password = _required("QA_RABBITMQ_PASSWORD")
            rabbitmq_url = f"amqp://{user}:{password}@{host}:{port}/"

        return cls(
            backend_url=_required("QA_BACKEND_URL").rstrip("/"),
            postgres_dsn=postgres_dsn,
            redis_url=redis_url,
            elasticsearch_url=_required("QA_ELASTICSEARCH_URL").rstrip("/"),
            s3_endpoint=_required("QA_S3_ENDPOINT").rstrip("/"),
            s3_access_key=_required("QA_S3_ACCESS_KEY"),
            s3_secret_key=_required("QA_S3_SECRET_KEY"),
            s3_bucket=_required("QA_S3_BUCKET"),
            rabbitmq_url=rabbitmq_url,
            es_index=os.getenv("QA_ELASTICSEARCH_INDEX", "documents"),
        )


def make_pdf_bytes(text: str) -> bytes:
    """Build a small valid PDF containing searchable ASCII text without extra deps."""
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(('BT /F1 14 Tf 72 720 Td (' + escaped + ') Tj ET').encode('latin-1'))} >>\nstream\nBT /F1 14 Tf 72 720 Td ({escaped}) Tj ET\nendstream",
    ]
    chunks = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(sum(len(c) for c in chunks))
        chunks.append(f"{number} 0 obj\n{obj}\nendobj\n".encode("latin-1"))
    xref_offset = sum(len(c) for c in chunks)
    xref = [f"xref\n0 {len(objects) + 1}\n", "0000000000 65535 f \n"]
    xref.extend(f"{offset:010d} 00000 n \n" for offset in offsets[1:])
    chunks.append("".join(xref).encode("ascii"))
    chunks.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return b"".join(chunks)


def cache_key(user_id: UUID | str, query: str) -> str:
    return f"search:{user_id}:{hashlib.md5(query.encode()).hexdigest()}"


async def eventually(
    assertion: Callable[[], Awaitable[None]], timeout: float = 20.0, interval: float = 0.4
) -> None:
    deadline = time.monotonic() + timeout
    last_error: BaseException | None = None
    while time.monotonic() < deadline:
        try:
            await assertion()
            return
        except AssertionError as error:
            last_error = error
            await asyncio.sleep(interval)
    if last_error:
        raise last_error


@pytest.fixture
def qa_settings() -> QASettings:
    return QASettings.from_env()


@pytest.fixture
async def qa_http(qa_settings: QASettings):
    async with httpx.AsyncClient(base_url=qa_settings.backend_url, timeout=30.0) as client:
        yield client


@pytest.fixture
async def qa_pg(qa_settings: QASettings):
    connection = await asyncpg.connect(qa_settings.postgres_dsn)
    try:
        yield connection
    finally:
        await connection.close()


@pytest.fixture
async def qa_redis(qa_settings: QASettings):
    client = redis.from_url(qa_settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
async def qa_es(qa_settings: QASettings):
    client = AsyncElasticsearch(qa_settings.elasticsearch_url)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
def qa_s3(qa_settings: QASettings):
    client = boto3.client(
        "s3",
        endpoint_url=qa_settings.s3_endpoint,
        aws_access_key_id=qa_settings.s3_access_key,
        aws_secret_access_key=qa_settings.s3_secret_key,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )
    try:
        client.head_bucket(Bucket=qa_settings.s3_bucket)
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code")
        if code in {"404", "NoSuchBucket"}:
            client.create_bucket(Bucket=qa_settings.s3_bucket)
        else:
            raise
    return client


@pytest.fixture
async def qa_users(qa_http: httpx.AsyncClient, qa_pg, qa_settings: QASettings, qa_s3, qa_es, qa_redis):
    """Factory for unique real users plus cleanup limited to their QA prefix."""
    created: list[dict[str, Any]] = []

    async def create_user() -> dict[str, Any]:
        username = f"{QA_PREFIX}{uuid4().hex[:16]}"
        response = await qa_http.post("/api/v1/registration", json={"username": username, "password": PASSWORD})
        assert response.status_code == 201, response.text
        data = response.json()
        login = await qa_http.post("/api/v1/login", json={"username": username, "password": PASSWORD})
        assert login.status_code == 200, login.text
        client = httpx.AsyncClient(base_url=qa_settings.backend_url, timeout=30.0)
        client.cookies.update(login.cookies)
        item = {"username": username, "user_id": UUID(data["user_id"]), "client": client}
        created.append(item)
        return item

    try:
        yield create_user
    finally:
        for item in created:
            user_id = str(item["user_id"])
            await item["client"].aclose()
            async for key in qa_redis.scan_iter(match=f"search:{user_id}:*"):
                await qa_redis.delete(key)
            try:
                await qa_es.delete_by_query(
                    index=qa_settings.es_index,
                    body={"query": {"term": {"user_id": user_id}}},
                    refresh=True,
                    conflicts="proceed",
                )
            except Exception:
                pass
            try:
                listed = qa_s3.list_objects_v2(Bucket=qa_settings.s3_bucket, Prefix=f"{user_id}/")
                keys = [{"Key": entry["Key"]} for entry in listed.get("Contents", [])]
                if keys:
                    qa_s3.delete_objects(Bucket=qa_settings.s3_bucket, Delete={"Objects": keys, "Quiet": True})
            except Exception:
                pass
            await qa_pg.execute("DELETE FROM users WHERE user_id = $1", item["user_id"])


async def upload_pdf(client: httpx.AsyncClient, name: str, text: str) -> UUID:
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": (name, make_pdf_bytes(text), "application/pdf")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "uploaded"
    return UUID(body["doc_id"])


async def es_user_doc_count(qa_es: AsyncElasticsearch, index: str, user_id: UUID, doc_id: UUID) -> int:
    result = await qa_es.count(
        index=index,
        query={"bool": {"filter": [{"term": {"user_id": str(user_id)}}, {"term": {"doc_id": str(doc_id)}}]}},
    )
    return int(result["count"])
