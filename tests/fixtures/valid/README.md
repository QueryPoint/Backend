# valid
См. `tests/docs/TEST_DATA_CATALOG.md`.

## Файлы
- `valid_multipage_ru.pdf` — валидный 3-страничный PDF с русским текстом (шрифт Arial), успешно извлекается pdfplumber постранично.
- `valid_nonstandard_font.pdf` — валидный PDF со встроенным нестандартным шрифтом (Times New Roman), проверяет независимость извлечения текста от шрифта.
- `valid_simple.docx` — валидный DOCX (python-docx), несколько абзацев русского текста, корректная OOXML/ZIP-структура.

Сгенерировано `reportlab`/`python-docx`; MIME проверен реальным `python-magic` (libmagic 5.48), извлечение текста проверено через `src/core/elasticsearch/extractor.py`.
