# Отчёт покрытия

Прогон (06.07.2026):
```bash
uv run pytest tests/unit tests/api tests/websocket --cov=src --cov-report=term-missing --cov-report=html
```
Результат: **91 passed**, общее покрытие **76%** (958 строк, 226 непокрыто). Интеграционные/health/load/e2e-наборы не участвуют в подсчёте (требуют реальной инфраструктуры/стенда — см. `QA_RUN_GUIDE.md`).

| Модуль | Покрытие | Комментарий |
|---|---:|---|
| `api/auth/security.py` | 100% | JWT/hash/verify |
| `api/auth/schemas.py` | 100% | границы username/password |
| `api/documents/service.py` | 51% | моки S3/ES/UoW — покрыт upload/validate, слабее покрыты list/get/delete-ветки |
| `core/elasticsearch/es_servise.py` | 88% | chunk/index/search, включая пагинацию (`limit`/`offset`) и highlight-теги `<mark>` |
| `core/elasticsearch/extractor.py` | 91% | извлечение текста PDF/DOCX |
| `api/search/service.py` | 100% | cache hit/miss, пагинация в cache-key |
| `core/ws/manager.py` | 100% | менеджер соединений |
| `core/ws/state.py` | 89% | состояние WS-сессии |

Ниже среднего покрыты `core/db/repositories/*` (41-62%) и `core/rabbitmq/*` (35-59%) — это в основном тонкие обёртки над реальными PostgreSQL/RabbitMQ клиентами, которые сознательно не мокаются построчно в unit-тестах (см. `TEST_PLAN.md`: такие сценарии переносятся в `tests/integration`, запускаются только с `QA_INTEGRATION=1`).

Не включай в процент покрытия файлы виртуального окружения, `.idea` и generated code.
