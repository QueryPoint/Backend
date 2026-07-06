# corrupted
См. `tests/docs/TEST_DATA_CATALOG.md`.

## Файлы
- `corrupted_broken_stream.pdf` — валидный по сигнатуре PDF (magic → `application/pdf`), но с испорченными байтами внутри content-стримов; `pdfplumber.open()` бросает `PdfminerException` при извлечении.
- `corrupted_broken_zip.docx` — валидный по сигнатуре DOCX/ZIP (magic → `application/vnd...wordprocessingml.document`), но с испорченными байтами внутри ZIP-записей; `docx.Document()` бросает `BadZipFile` (Bad CRC-32).

Оба файла проходят проверку MIME на этапе загрузки, но должны падать на этапе извлечения текста (`extract_pages`) — так и происходит при ручной проверке.
