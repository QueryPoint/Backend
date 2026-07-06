# E2E-тестирование фронтенда через Playwright + pytest

## Что проверяет Playwright

Playwright запускает настоящий браузер и повторяет действия пользователя:
переходы по страницам, ввод данных, клики, выбор файла и проверку видимого
результата. В `pytest-playwright` фикстура `page` создаёт отдельную вкладку в
изолированном browser context для каждого теста.

В этом проекте цепочка должна быть такой:

```text
Playwright / Windows → Frontend Vite :5173 → proxy /api → Backend :8000
                                      Backend → Docker network → PostgreSQL, Redis,
                                                                  Elasticsearch, RabbitMQ, MinIO
```

Порт `8000` принадлежит backend. Это не адрес, который браузер должен открывать
как интерфейс: браузер открывает frontend на `5173` в dev-режиме. Vite направляет
AJAX-запросы с `/api` на backend.

## Первичная установка

В репозитории backend тестовые зависимости должны включать `pytest-playwright`.
После обновления `pyproject.toml`:

```powershell
cd "C:\path\to\pp backend\Backend"
uv lock
uv sync --group test
uv run --group test playwright install chromium
```

Установка Python-пакета и установка браузера — две разные операции. Браузер
нужен Playwright отдельно.

## Как писать тест

```python
from playwright.sync_api import expect


def test_login_button_is_visible(page):
    page.goto("http://127.0.0.1:5173/login")
    expect(page.get_by_role("button", name="Войти")).to_be_visible()
```

Главные операции:

```python
page.goto(url)                              # открыть страницу
page.get_by_role("button", name="...").click()
page.get_by_placeholder("...").fill("...")
page.locator("input[type=file]").set_input_files(path)
expect(locator).to_be_visible()             # ожидание и проверка
expect(page).to_have_url("**/documents")
```

`expect(...)` лучше, чем `time.sleep()`: Playwright сам ждёт появления элемента
в пределах заданного таймаута.

## Режимы запуска

Обычный headless-прогон:

```powershell
$env:QA_E2E = "1"
$env:E2E_BASE_URL = "http://127.0.0.1:5173"
uv run --group test pytest -c tests/pytest.ini tests/e2e -v --browser chromium
```

Видимый браузер для отладки:

```powershell
uv run --group test pytest -c tests/pytest.ini tests/e2e/test_auth_e2e.py -v --browser chromium --headed
```

Только один тест:

```powershell
uv run --group test pytest -c tests/pytest.ini `
  tests/e2e/test_public_pages_e2e.py::test_registration_blocks_mismatched_passwords -v --browser chromium
```

Генератор черновика теста:

```powershell
uv run --group test playwright codegen http://127.0.0.1:5173
```

Сгенерированный код нужно затем очистить: оставить устойчивые locator'ы по role,
label, placeholder или `data-testid`, добавить `expect(...)` и удалить лишние
действия.

## Артефакты неуспешного прогона

```powershell
uv run --group test pytest -c tests/pytest.ini tests/e2e -v --browser chromium `
  --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure `
  --output test-results/e2e
```

Trace открывается так:

```powershell
uv run --group test playwright show-trace .\test-results\e2e\trace.zip
```

## Обязательное правило безопасности

E2E выполняется только с `QA_E2E=1` и на локальном/QA стенде. Тесты создают
пользователей и документы. Не указывай production URL в `E2E_BASE_URL` и не
подключай production базу/MinIO.
