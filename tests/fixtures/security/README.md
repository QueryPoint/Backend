# security
См. `tests/docs/TEST_DATA_CATALOG.md`.

## Файлы
- `macro_enabled_document.docm` — макрос-контейнер: OOXML/ZIP с `word/vbaProject.bin` и content-type `macroEnabled.main+xml`; magic определяет его как DOCX MIME, что и является предметом будущей security-проверки (расширение/контент не совпадают с обычным `.docx`).
- `%2e%2e%2fpasswd.pdf` — суррогат path traversal-имени: файловая система (APFS/macOS) не позволяет создать буквальное имя с `../` внутри одного компонента пути, поэтому использован percent-encoded вариант (`%2e%2e%2f` = `../`). Реальный traversal-паттерн нужно тестировать через сам HTTP-запрос (в `filename` из `multipart/form-data`), а не через имя файла на диске.
- `zip_bomb_surrogate.zip` — суррогат zip bomb: 8MB нулевых байт сжаты в ~8KB (коэффициент сжатия ~1000x), достаточно для проверки защиты от распаковки без риска реального исчерпания диска/памяти в тестовой среде.
