# Итоговый QA-отчёт

## Объект
Backend интеллектуальной базы знаний, ветка `feature/docs-ws`.

## Ограничение
Тесты добавлены только в `/tests`; backend-файлы не редактировались.

## Выполненные наборы
- Unit: auth, schemas, cookies, documents, parsers, chunking, S3, Elasticsearch, Redis, search, RabbitMQ, WS state.
- API: auth/documents/search/history/ping с dependency overrides.
- WebSocket: authentication helper, prompt/processing/delete, connection manager.
- Health: внешний backend/PostgreSQL/Redis/ES/S3/RabbitMQ.
- Integration: подготовлены и намеренно пропускаются без отдельного стенда.
- Load: Locust-сценарий поиска.

## Зафиксированные риски/расхождения текущего backend
1. Нет `/health` и `/ready`; доступность backend проверяется через `GET /`.
2. Нет read endpoint для search history.
3. Search не валидирует пустую строку `q=` и не имеет пагинации/фильтров.
4. Upload проверяет MIME и размер, но нет явной проверки PDF signature, DOCX ZIP structure, docm/zip bomb/path traversal.
5. `secure=False` у auth cookies — приемлемо для localhost, но небезопасно для production.
6. `Redis.url` использует `self.DB`, которого нет в модели `Redis`: потенциальная runtime-ошибка.
7. Нет отдельных status-events обработки документа; индексация синхронная в upload.

## Итог
Финальный статус и количественные результаты заполняются после запуска команд из `QA_RUN_GUIDE.md` на окружении с `uv` и доступными сервисами.
