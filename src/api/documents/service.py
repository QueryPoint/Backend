from uuid import UUID, uuid4

import magic
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from src.config.config import config
from src.core.db.uow import UnitOfWork
from src.core.db.enums import DocType
from src.core.db.dto.docDTO import DocumentDTO, DocumentDetailDTO
from src.core.s3.s3_service import s3_service
from src.core.elasticsearch.extractor import extract_pages
from src.core.elasticsearch.es_servise import elastic_service
from src.api.exc.documents import InvalidDocument, DocumentNotFound, DocumentForbidden, S3Error

MAX_FILE_SIZE = 20 * 1024 * 1024
PRESIGNED_TTL = 15 * 60

ALLOWED_MIME = {
    "application/pdf": DocType.pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocType.docx,
}


class DocumentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _build_key(user_id: UUID, doc_id: UUID, doc_type: DocType) -> str:
        return f"{user_id}/{doc_id}.{doc_type.value}"

    async def upload(self, user_id: UUID, file: UploadFile) -> DocumentDTO:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise InvalidDocument

        mime = magic.from_buffer(content, mime=True)
        doc_type = ALLOWED_MIME.get(mime)
        if doc_type is None:
            raise InvalidDocument

        doc_id = uuid4()
        key = self._build_key(user_id, doc_id, doc_type)

        ok = await run_in_threadpool(s3_service.upload_file, content, key)
        if not ok:
            raise S3Error

        viewlink = f"{config.s3.ENDPOINT_URL}/{config.s3.BUCKET_NAME}/{key}"

        doc = await self.uow.document.create(
            doc_id=doc_id,
            user_id=user_id,
            doc_name=file.filename,
            doc_viewlink=viewlink,
            doc_size=len(content),
            doc_type=doc_type,
        )

        pages = await run_in_threadpool(extract_pages, content, doc_type)
        for page_number, page_text in pages:
            await elastic_service.index_chunks(
                doc_id=doc_id,
                user_id=user_id,
                file_name=file.filename,
                text=page_text,
                page_number=page_number,
            )

        return doc

    async def list(self, user_id: UUID, limit: int, offset: int, filename: str | None) -> list[DocumentDTO]:
        return await self.uow.document.list(user_id, limit, offset, filename)

    async def get_one(self, user_id: UUID, doc_id: UUID) -> DocumentDetailDTO:
        doc = await self.uow.document.get_by_id(doc_id)
        if doc is None:
            raise DocumentNotFound
        if doc.user_id != user_id:
            raise DocumentForbidden

        key = self._build_key(doc.user_id, doc.doc_id, doc.doc_type)
        link = await run_in_threadpool(s3_service.generate_presigned_url, key, PRESIGNED_TTL)
        if link is None:
            raise S3Error

        return DocumentDetailDTO(
            doc_id=doc.doc_id,
            doc_name=doc.doc_name,
            doc_viewlink=doc.doc_viewlink,
            doc_size=doc.doc_size,
            doc_type=doc.doc_type.value,
            doc_downloadlink=link,
        )

    async def delete(self, user_id: UUID, doc_id: UUID) -> None:
        doc = await self.uow.document.get_by_id(doc_id)
        if doc is None:
            raise DocumentNotFound
        if doc.user_id != user_id:
            raise DocumentForbidden

        key = self._build_key(doc.user_id, doc.doc_id, doc.doc_type)
        await self.uow.document.delete(doc)

        await run_in_threadpool(s3_service.delete_file, key)
        await elastic_service.delete_chunks(doc_id=doc_id)