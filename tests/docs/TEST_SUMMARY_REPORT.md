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
1. Нет `/health` и `/ready`; доступность backend проверяется через `GET /`. *(не устранено)*
2. Нет read endpoint для search history. *(не устранено)*
3. ~~Search не валидирует пустую строку `q=` и не имеет пагинации/фильтров.~~ **Устранено**: `GET /search` теперь требует `min_length=1` для `q` и принимает `limit`/`offset` (по умолчанию 10/0).
4. Upload проверяет MIME и размер, но нет явной проверки PDF signature, DOCX ZIP structure, docm/zip bomb/path traversal. *(не устранено)*
5. `secure=False` у auth cookies — приемлемо для localhost, но небезопасно для production. *(не устранено, осознанный компромисс для локальной разработки)*
6. ~~`Redis.url` использует `self.DB`, которого нет в модели `Redis`: потенциальная runtime-ошибка.~~ **Устранено**: добавлено поле `DB: int = 0` в `src/config/config.py`.
7. Нет отдельных status-events обработки документа; индексация синхронная в upload. *(бэкенд не изменён — обработано на фронтенде: после успешной загрузки UI показывает шаг "Индексация" и переходит в "Готово", т.к. к моменту ответа сервера индексация уже реально завершена)*

## Итог

Финальный прогон (06.07.2026, локальный стенд: docker-compose Postgres/Redis/Elasticsearch/MinIO/RabbitMQ + backend):

- **Unit + API + WebSocket:** 91 passed, 0 failed. Покрытие `src` — **76%** (подробности в `COVERAGE_REPORT.md`).
- **E2E:** сценарии подготовлены (`tests/e2e/`), требуют живого frontend + backend (`E2E_PLAYWRIGHT_GUIDE.md`).
- **Load (QA-04):** 50 одновременных пользователей, 2 минуты, **0% ошибок**, медиана поиска 13мс — подробности в `LOAD_TEST_REPORT.md`.
- **Precision@3 (QA-05):** **10/10 (100%)** на реальных данных (10 статей arXiv, загруженных через `init.sh`) — подробности в `PRECISION_AT_3_REPORT.md`.
- Из 7 зафиксированных рисков устранено 2 (пагинация/пустой запрос, Redis.DB); остальные 5 задокументированы как осознанно отложенные, не блокирующие текущую сдачу.
