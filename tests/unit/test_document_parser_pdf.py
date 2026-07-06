
from unittest.mock import MagicMock, patch
from src.core.elasticsearch.extractor import _extract_pdf

def test_pdf_parser_returns_only_nonempty_pages():
    page1, page2 = MagicMock(), MagicMock()
    page1.extract_text.return_value = "Текст первой страницы"
    page2.extract_text.return_value = "   "
    pdf = MagicMock()
    pdf.pages = [page1, page2]
    with patch("src.core.elasticsearch.extractor.pdfplumber.open") as open_pdf:
        open_pdf.return_value.__enter__.return_value = pdf
        assert _extract_pdf(b"pdf") == [(1, "Текст первой страницы")]

def test_pdf_parser_preserves_page_numbers_after_empty_page():
    pages = [MagicMock(), MagicMock(), MagicMock()]
    pages[0].extract_text.return_value = ""
    pages[1].extract_text.return_value = "page two"
    pages[2].extract_text.return_value = "page three"
    pdf = MagicMock(pages=pages)
    with patch("src.core.elasticsearch.extractor.pdfplumber.open") as open_pdf:
        open_pdf.return_value.__enter__.return_value = pdf
        assert _extract_pdf(b"x") == [(2, "page two"), (3, "page three")]
