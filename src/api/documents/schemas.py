from uuid import UUID
from pydantic import BaseModel

class DocumentUploadResponse(BaseModel):
    status: str
    doc_id: str

class DocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    doc_id: UUID
    doc_name: str
    doc_viewlink: str
    doc_size: int
    doc_type: str

class DocumentDetailData(BaseModel):
    model_config = {"from_attributes": True}

    doc_id: UUID
    doc_name: str
    doc_viewlink: str
    doc_size: int
    doc_type: str
    doc_downloadlink: str

class DocumentDetailResponse(BaseModel):
    data: DocumentDetailData