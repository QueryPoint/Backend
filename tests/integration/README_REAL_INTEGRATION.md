# Реальные интеграционные тесты

Файлы в этой директории не используют mock, monkeypatch или fake-клиенты.
Они отправляют HTTP/WebSocket запросы в поднятый backend и подключаются к
реальным PostgreSQL, Redis, Elasticsearch, S3/MinIO и RabbitMQ.

## Защита от случайного запуска

Тесты выполняются только при явном флаге:

```powershell
$env:QA_REAL_INTEGRATION = "1"
```

Без него каждый тест будет `SKIPPED` — это безопасное штатное поведение.

## Обязательные параметры

Перед запуском укажи тестовые, а не production, значения:

```powershell
$env:QA_BACKEND_URL = "http://127.0.0.1:8000"
$env:QA_POSTGRES_DSN = "postgresql://qa_user:qa_password@127.0.0.1:5432/querypoint_test"
$env:QA_REDIS_URL = "redis://:qa_password@127.0.0.1:6379/1"
$env:QA_ELASTICSEARCH_URL = "http://127.0.0.1:9200"
$env:QA_ELASTICSEARCH_INDEX = "documents_test"
$env:QA_S3_ENDPOINT = "http://127.0.0.1:9000"
$env:QA_S3_ACCESS_KEY = "qa_access_key"
$env:QA_S3_SECRET_KEY = "qa_secret_key"
$env:QA_S3_BUCKET = "querypoint-qa"
$env:QA_RABBITMQ_URL = "amqp://qa_user:qa_password@127.0.0.1:5672/"
$env:QA_REAL_INTEGRATION = "1"
```

Сервисы должны быть доступны с той машины, где запускается pytest. При
запуске из Windows это обычно `127.0.0.1` и проброшенные Docker-порты, а не
внутренние имена контейнеров `querypoint_postgres`, `querypoint_redis` и т.д.

## Команда

```powershell
uv run --group test pytest tests/integration -v
```

Тесты создают пользователей с префиксом `qait_`, объекты только в пределах
папки `<user_id>/` указанного тестового bucket и очищают свои PostgreSQL,
Redis, S3 и Elasticsearch данные в teardown. Не выдавай им доступ к
production-среде.

## Покрываемые реальные цепочки

- upload API → S3/MinIO → PostgreSQL → extraction → Elasticsearch;
- search API → PostgreSQL history → Redis cache → Elasticsearch;
- document delete API → PostgreSQL + S3/MinIO + Elasticsearch;
- доступ одного пользователя к документам другого;
- RabbitMQ `llm_to_back` → backend consumer → Redis connection state → WebSocket.
