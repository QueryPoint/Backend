# План тестирования backend

## Объект
Backend интеллектуальной базы знаний, ветка `feature/docs-ws`. QA-код расположен только в `/tests`; исходный backend не изменяется.

## Уровни
- **Unit:** JWT, схемы, cookies, file validation, PDF/DOCX extraction, chunking, S3, Elasticsearch, Redis, поиск, RabbitMQ, WebSocket state.
- **API:** маршруты FastAPI и коды ответов через dependency overrides.
- **Integration:** реальные PostgreSQL/S3/Elasticsearch/Redis/RabbitMQ; запускаются только с `QA_INTEGRATION=1`.
- **WebSocket:** access cookie, prompt flow, processing/blocked/idle, manager.
- **Health:** внешняя доступность сервисов через env.
- **Load:** Locust, 50 одновременных пользователей.

## Критерии
Критические unit/API тесты должны проходить. Integration/health допускается пропускать локально только при отсутствии выделенного тестового окружения; в отчёте это фиксируется как ограничение.
