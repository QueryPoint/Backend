# Исправление bootstrap для Windows и пустого config.toml

## Почему были ошибки при collection

1. `python-magic` на Windows требует native-библиотеку `libmagic.dll`.
2. Backend создаёт Elasticsearch-клиент при импорте модуля. Если в `config.toml`
   URL Elasticsearch пустой, библиотека Elasticsearch прекращает работу ещё до
   запуска тестов.

## Что делает исправленный tests/conftest.py

Он выполняется до импорта тестовых модулей и только во время pytest-run:

- подставляет test-only stub модуля `magic`;
- задаёт безопасные синтаксически корректные тестовые значения конфигурации;
- не подключается к реальным сервисам;
- не меняет backend-файлы и не требует правки `config.toml`.

## Запуск

```powershell
uv sync --group test
uv run --group test pytest tests -v
```

Не запускайте после этого обычный `uv sync`, если хотите оставить test-group
установленной в виртуальной среде: обычный sync синхронизирует только default
группы и удаляет необязательные test-зависимости. Вместо этого всегда используйте
`uv sync --group test`.
