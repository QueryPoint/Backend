from uuid import UUID
from typing import Optional

from fastapi import APIRouter, UploadFile, Depends, Query

from src.api.auth.dependencies import get_current_user_id
from src.api.documents.dependencies import get_document_service
from src.api.documents.service import DocumentService
from src.api.documents.schemas import (
    DocumentUploadResponse, DocumentResponse,
    DocumentDetailResponse, DocumentDetailData,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile,
    user_id: UUID = Depends(get_current_user_id),
    service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    doc = await service.upload(user_id, file)
    return DocumentUploadResponse(status="uploaded", doc_id=str(doc.doc_id))


@router.get("", response_model=list[DocumentResponse], status_code=200)
async def list_documents(
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    filename: Optional[str] = Query(default=None),
    user_id: UUID = Depends(get_current_user_id),
    service: DocumentService = Depends(get_document_service),
):
    return await service.list(user_id, limit, offset, filename)


@router.get("/{doc_id}", response_model=DocumentDetailResponse, status_code=200)
async def get_document(
    doc_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DocumentService = Depends(get_document_service),
) -> DocumentDetailResponse:
    doc = await service.get_one(user_id, doc_id)
    return DocumentDetailResponse(data=DocumentDetailData.model_validate(doc))


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: DocumentService = Depends(get_document_service),
) -> None:
    await service.delete(user_id, doc_id)