# QueryPoint — Backend

Бэкенд интеллектуальной поисковой системы по внутренней базе знаний университета.
Реализует загрузку и обработку документов, полнотекстовый поиск с подсветкой
совпадений, историю запросов и AI-ассистента через WebSocket.

## Стек

- **Python 3.12**, **FastAPI** (async/await)
- **PostgreSQL** + **SQLAlchemy 2.0** (asyncpg) — метаданные
- **Elasticsearch** — индексация чанков и полнотекстовый поиск (русский анализатор)
- **Redis** — кэш поиска, сессии WebSocket, временные статусы
- **RabbitMQ** — обмен сообщениями с LLM-сервисом
- **S3 / MinIO** (boto3) — хранение оригиналов документов
- **JWT в cookie** + **bcrypt** — авторизация
- **Prometheus** (`prometheus-fastapi-instrumentator`) — метрики

## Архитектура

Слоистая архитектура:

```text
src/
├── api/            # API-слой: роутеры, схемы, сервисы, обработка ошибок
│   ├── auth/       # регистрация, логин, refresh, logout, профиль
│   ├── documents/  # загрузка, список, получение, удаление документов
│   ├── search/     # полнотекстовый поиск, история
│   ├── ws/         # WebSocket-эндпоинт
│   └── exc/        # доменные исключения → HTTP-статусы
├── core/           # инфраструктура
│   ├── db/         # модели, репозитории, DTO, Unit of Work
│   ├── elasticsearch/
│   ├── redis/
│   ├── rabbitmq/
│   ├── s3/
│   └── ws/         # менеджер соединений и статусов
├── config/         # загрузка конфигурации
└── main.py         # точка входа FastAPI
```

## Хранение данных

- **PostgreSQL** — пользователи, хэши паролей, метаданные документов, история поиска
- **S3/MinIO** — оригиналы файлов
- **Elasticsearch** — текстовые чанки
- **Redis** — кэш поиска, mapping `user_id → ws_conn_id`, статусы WebSocket

## Требования

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- Запущенные PostgreSQL, Elasticsearch, Redis, RabbitMQ, S3/MinIO
- Системная библиотека `libmagic` (для проверки MIME)

## Конфигурация

Скопируй пример конфига и заполни значения:

```bash
cp config.example.toml config.toml
```

Секции: `[database]`, `[s3]`, `[jwt]`, `[elasticsearch]`, `[redis]`, `[rabbitmq]`, `[cors]`.

## Запуск

Локально:

```bash
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

В Docker:

```bash
docker compose up --build
```

После старта:

- Swagger UI — `http://localhost:8000/docs`
- Метрики Prometheus — `http://localhost:8000/metrics`

## REST API

Базовый префикс: `/api/v1`

### Аутентификация

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/v1/registration` | Регистрация пользователя |
| POST | `/api/v1/login` | Логин, установка cookie |
| POST | `/api/v1/refresh` | Обновление access-сессии |
| POST | `/api/v1/logout` | Выход, сброс cookie |
| GET | `/api/v1/me` | Профиль + документы (пагинация) |

### Документы

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/v1/documents/upload` | Загрузка PDF/DOCX (≤20 МБ) |
| GET | `/api/v1/documents` | Список документов (пагинация, поиск по имени) |
| GET | `/api/v1/documents/{doc_id}` | Метаданные + presigned URL (TTL 15 мин) |
| DELETE | `/api/v1/documents/{doc_id}` | Удаление из PostgreSQL, S3 и Elasticsearch |

### Поиск

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/v1/search?q={query}` | Полнотекстовый поиск с подсветкой (кэш Redis, TTL 300 с) |
| DELETE | `/api/v1/history` | Очистка истории поиска |

### WebSocket

| Путь | Описание |
|---|---|
| `/api/v1/ws` | AI-ассистент: авторизация по cookie, статусы `idle/processing/blocked`, обмен с LLM через RabbitMQ |

## Обработка документов

1. Проверка размера (≤20 МБ) и реального MIME-типа через `python-magic`
2. Загрузка оригинала в S3/MinIO
3. Сохранение метаданных в PostgreSQL
4. Извлечение текста: `pdfplumber` (PDF) / `python-docx` (DOCX)
5. Нарезка на чанки по 1000 символов с overlap 100
6. Индексация чанков в Elasticsearch

## Тестирование

```bash
# юнит + API + websocket (без внешних сервисов)
uv run pytest tests/unit tests/api tests/websocket

# интеграционные (нужны живые сервисы)
QA_REAL_INTEGRATION=1 uv run pytest tests/integration

# health-проверки
QA_HEALTH=1 uv run pytest tests/health

# e2e (Playwright, нужен поднятый стек)
uv run pytest tests/e2e
```

## Безопасность

- Все защищённые эндпоинты и WebSocket проверяют одну и ту же cookie-сессию
- Пользователь имеет доступ только к своим документам (иначе `403 Forbidden`)
- `user_id` берётся из сессии, а не из тела запроса
- Пароли хэшируются через `bcrypt`
- MIME-тип файла проверяется по содержимому, а не по расширению
- Presigned URL на скачивание имеет ограниченный TTL