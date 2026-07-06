
from uuid import uuid4
from unittest.mock import AsyncMock
import pytest
from fastapi import UploadFile
from io import BytesIO

from src.api.documents.service import DocumentService, MAX_FILE_SIZE
from src.api.exc.documents import InvalidDocument

pytestmark = pytest.mark.unit

def upload(name, content):
    return UploadFile(filename=name, file=BytesIO(content))

@pytest.mark.asyncio
async def test_upload_rejects_file_larger_than_limit(fake_uow, user_id):
    service = DocumentService(fake_uow)
    with pytest.raises(InvalidDocument):
        await service.upload(user_id, upload("too_large.pdf", b"x"*(MAX_FILE_SIZE+1)))

@pytest.mark.asyncio
async def test_upload_rejects_empty_file(fake_uow, user_id, monkeypatch):
    monkeypatch.setattr("src.api.documents.service.magic.from_buffer", lambda *a, **k: "application/octet-stream")
    service = DocumentService(fake_uow)
    with pytest.raises(InvalidDocument):
        await service.upload(user_id, upload("empty.pdf", b""))

@pytest.mark.asyncio
@pytest.mark.parametrize("mime", ["text/plain", "application/zip", "image/png", None])
async def test_upload_rejects_unsupported_mime(fake_uow, user_id, monkeypatch, mime):
    monkeypatch.setattr("src.api.documents.service.magic.from_buffer", lambda *a, **k: mime)
    service = DocumentService(fake_uow)
    with pytest.raises(InvalidDocument):
        await service.upload(user_id, upload("bad.bin", b"data"))

def test_build_key_is_user_and_document_scoped(user_id, other_user_id):
    doc_id = uuid4()
    from src.core.db.enums import DocType
    key = DocumentService._build_key(user_id, doc_id, DocType.pdf)
    assert str(user_id) in key and str(doc_id) in key and key.endswith(".pdf")
    assert str(other_user_id) not in key
