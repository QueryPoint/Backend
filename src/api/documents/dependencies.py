from typing import AsyncIterator

from src.core.db.uow import get_uow
from src.api.documents.service import DocumentService


async def get_document_service() -> AsyncIterator[DocumentService]:
    async with get_uow() as uow:
        yield DocumentService(uow)