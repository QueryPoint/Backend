# Отчёт покрытия

Заполняется после прогона:
```bash
uv run pytest tests --cov=src --cov-report=term-missing --cov-report=html
```

| Модуль | Покрытие | Комментарий |
|---|---:|---|
| `api/auth/security.py` | — | JWT/hash/verify |
| `api/auth/schemas.py` | — | границы username/password |
| `api/documents/service.py` | — | моки S3/ES/UoW |
| `core/elasticsearch/*` | — | chunk/index/search |
| `api/search/service.py` | — | cache hit/miss |
| `core/ws/*` | — | state/manager |

Не включай в процент покрытия файлы виртуального окружения, `.idea` и generated code.
