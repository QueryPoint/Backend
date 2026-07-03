
from unittest.mock import MagicMock, patch
from src.core.elasticsearch.extractor import _extract_docx, extract_pages
from src.core.db.enums import DocType

def test_docx_parser_joins_nonempty_paragraphs():
    doc = MagicMock()
    doc.paragraphs = [MagicMock(text="Заголовок"), MagicMock(text=""), MagicMock(text="Абзац")]
    with patch("src.core.elasticsearch.extractor.docx.Document", return_value=doc):
        assert _extract_docx(b"docx") == [(1, "Заголовок\nАбзац")]

def test_docx_parser_returns_empty_for_empty_document():
    doc = MagicMock()
    doc.paragraphs = [MagicMock(text=" "), MagicMock(text="")]
    with patch("src.core.elasticsearch.extractor.docx.Document", return_value=doc):
        assert _extract_docx(b"docx") == []

def test_extract_pages_returns_empty_for_unknown_doc_type():
    assert extract_pages(b"data", object()) == []
