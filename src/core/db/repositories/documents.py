from uuid import UUID

from sqlalchemy import select

from src.core.db.models.documents import Document
from src.core.db.enums import DocType
from src.core.db.dto.docDTO import DocumentDTO
from src.core.db.repositories.base import BaseRepository


class DocRepository(BaseRepository):

    async def create(
        self,
        doc_id: UUID,
        user_id: UUID,
        doc_name: str,
        doc_viewlink: str,
        doc_size: int,
        doc_type: DocType,
    ) -> DocumentDTO:
        doc = Document(
            doc_id=doc_id,
            user_id=user_id,
            doc_name=doc_name,
            doc_viewlink=doc_viewlink,
            doc_size=doc_size,
            doc_type=doc_type,
        )
        self._session.add(doc)
        await self._session.flush()
        return self._to_dto(doc)

    async def get_by_id(self, doc_id: UUID) -> Document | None:
        return await self._session.get(Document, doc_id)

    async def list(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
        filename: str | None = None,
    ) -> list[DocumentDTO]:
        stmt = select(Document).where(Document.user_id == user_id)
        if filename:
            stmt = stmt.where(Document.doc_name.ilike(f"%{filename}%"))
        stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return [self._to_dto(doc) for doc in result.scalars().all()]

    async def delete(self, doc: Document) -> None:
        await self._session.delete(doc)

    @staticmethod
    def _to_dto(doc: Document) -> DocumentDTO:
        return DocumentDTO(
            doc_id=doc.doc_id,
            doc_name=doc.doc_name,
            doc_viewlink=doc.doc_viewlink,
            doc_size=doc.doc_size,
            doc_type=doc.doc_type.value,
        )