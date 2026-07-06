# Playwright E2E suite

These tests automate a real Chromium browser against a running frontend and
backend. They are intentionally different from unit, API and integration
tests: a scenario is executed through visible controls as a user sees them.

## Preconditions

- Docker infrastructure, backend and MinIO are running and health checks pass.
- The frontend is running at `E2E_BASE_URL` (default: `http://127.0.0.1:5173`).
- `QA_E2E=1` is explicitly set.
- `pytest-playwright` and the Chromium binary are installed in the backend uv
environment.

## Windows / PowerShell quick run

In one PowerShell window, start the frontend development server:

```powershell
cd "C:\path\to\pp frontend\Frontend"
Copy-Item .env.example .env -Force
$env:VITE_API_PROXY_TARGET = "http://127.0.0.1:8000"
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

In a second PowerShell window, run the browser tests from the backend project:

```powershell
cd "C:\path\to\pp backend\Backend"
uv sync --group test
uv run --group test playwright install chromium

$env:QA_E2E = "1"
$env:E2E_BASE_URL = "http://127.0.0.1:5173"
$env:NO_PROXY = "127.0.0.1,localhost"
$env:no_proxy = $env:NO_PROXY

uv run --group test pytest -c tests/pytest.ini tests/e2e -v --browser chromium `
  --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure `
  --output test-results/e2e
```

For interactive debugging, add `--headed`:

```powershell
uv run --group test pytest -c tests/pytest.ini tests/e2e/test_auth_e2e.py -v `
  --browser chromium --headed --tracing on --screenshot on --output test-results/e2e-debug
```

## Scope

- Public routes and client-side validation.
- Registration, authenticated route and logout.
- PDF upload, document list and deletion.
- Search for an uploaded PDF.

The suite does not currently automate a complete assistant-answer scenario.
That scenario needs a real assistant/LLM worker that consumes RabbitMQ jobs and
returns a response; the supplied infrastructure contains RabbitMQ but not that
worker.

## Artifacts on failure

`pytest-playwright` writes screenshots, video and Playwright traces to the
path passed via `--output`. Open a saved trace with:

```powershell
uv run --group test playwright show-trace .\test-results\e2e\trace.zip
```

## Test design

The tests use accessible role/text locators and placeholders. The current UI
has no `data-testid` values, so changing text or placeholders can require a
locator update. New frontend components should preferably expose stable
`data-testid` attributes for non-textual controls such as upload zones and
document cards.
