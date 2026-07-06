import io

import pdfplumber
import docx

from src.core.db.enums import DocType

def extract_pages(content: bytes, doc_type: DocType) -> list[tuple[int, str]]:
    if doc_type == DocType.pdf:
        return _extract_pdf(content)
    if doc_type == DocType.docx:
        return _extract_docx(content)
    return []

def _extract_pdf(content: bytes) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((page_number, text))
    return pages

def _extract_docx(content: bytes) -> list[tuple[int, str]]:
    document = docx.Document(io.BytesIO(content))
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
    return [(1, text)] if text.strip() else []