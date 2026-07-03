# Запуск QA-набора через uv

## Установка uv
Windows PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```
Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

## Подготовка
В корне backend (где `pyproject.toml`):
```bash
uv sync
uv add --group test pytest pytest-asyncio pytest-cov httpx locust
```
Если нельзя менять `pyproject.toml`, используй временно:
```bash
uv run --with pytest --with pytest-asyncio --with pytest-cov --with httpx pytest tests/unit -v
```

## Запуск
```bash
uv run pytest tests/unit -v
uv run pytest tests/api -v
uv run pytest tests/websocket -v
uv run pytest tests/unit tests/api tests/websocket -v
uv run pytest tests --cov=src --cov-report=term-missing --cov-report=html
```

Integration (только на отдельном тестовом стенде):
```bash
QA_REAL_INTEGRATION=1 uv run pytest tests/integration -v
```
PowerShell:
```powershell
$env:QA_REAL_INTEGRATION = "1"
uv run pytest tests/integration -v
```

Health checks запускаются только с `QA_HEALTH=1` и задаются переменными
`QA_BACKEND_URL`, `QA_POSTGRES_HOST`, `QA_REDIS_HOST`, `QA_ELASTICSEARCH_URL`,
`QA_S3_HOST`, `QA_RABBITMQ_HOST`.

```bash
QA_HEALTH=1 QA_BACKEND_URL=http://localhost:8000 QA_ELASTICSEARCH_URL=http://localhost:9200 uv run pytest tests/health -v
```

Нагрузка 50 пользователей:
```bash
QA_LOAD_USERNAME=qa_user QA_LOAD_PASSWORD=123456 uv run locust -f tests/load/locustfile.py --host http://localhost:8000 --headless -u 50 -r 5 -t 2m
```

HTML покрытие: `htmlcov/index.html`.
