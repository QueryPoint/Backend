# invalid
См. `tests/docs/TEST_DATA_CATALOG.md`.

## Файлы
- `fake_extension_text_as_pdf.pdf` — обычный текст под расширением `.pdf` (magic → `text/plain`, должен быть отклонён).
- `fake_extension_jpg_as_pdf.pdf` — настоящий JPEG под расширением `.pdf` (magic → `image/jpeg`, должен быть отклонён).
- `plain_text_document.txt`, `real_image.jpg`, `real_archive.zip` — файлы с корректным расширением, но недопустимым для сервиса типом (TXT/JPG/ZIP).

Все MIME-типы подтверждены реальным `python-magic` (libmagic 5.48): ни один не входит в `ALLOWED_MIME` из `src/api/documents/service.py`.
