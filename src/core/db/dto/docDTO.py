from dataclasses import dataclass
from uuid import UUID


@dataclass
class DocumentDTO:
    doc_id: UUID
    doc_name: str
    doc_viewlink: str
    doc_size: int
    doc_type: str


@dataclass
class DocumentDetailDTO:
    doc_id: UUID
    doc_name: str
    doc_viewlink: str
    doc_size: int
    doc_type: str
    doc_downloadlink: str