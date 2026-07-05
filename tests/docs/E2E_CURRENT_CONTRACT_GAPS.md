# Текущие несовпадения frontend ↔ backend, которые блокируют full E2E

Набор E2E описывает ожидаемый пользовательский сценарий. На переданных версиях
frontend и backend положительные сценарии регистрации, загрузки и поиска пока
не пройдут до выравнивания контракта.

## P0: маршруты авторизации

Frontend (`src/services/authService.ts`) использует `/auth/register`,
`/auth/login`, `/auth/me`, `/auth/refresh`, `/auth/logout` с base URL `/api`.
Backend объявляет `POST /api/v1/registration`, `POST /api/v1/login`,
`GET /api/v1/me`, `POST /api/v1/refresh`, `POST /api/v1/logout`.

Следствие: браузер отправляет, например, `POST /api/auth/register`, но backend
не имеет такого маршрута.

## P0: структура ответа авторизации

Frontend обращается к `response.data.user`, а backend возвращает корневой объект
с `user_id` и `username`. Это надо привести к одной форме.

## P0: документы

Frontend вызывает `/documents` и отправляет multipart-поле `files`.
Backend использует `/api/v1/documents` и принимает одно поле `file`.

Frontend ожидает список в `res.data.items` и поля `id`, `file_name`, `file_type`,
`size`, `status`. Backend возвращает список и поля `doc_id`, `doc_name`,
`doc_type`, `doc_size`, `doc_viewlink`. Upload backend отвечает `{status, doc_id}`.

## P1: поиск

Frontend ожидает пагинацию `{items, has_more}`, поля `page`, `document_id` и
GET `/search/history`. Backend возвращает список с `page_number` и имеет только
DELETE `/api/v1/history`.

## P1: WebSocket ассистента

Frontend по умолчанию подключается к `/api/ws`, backend слушает `/api/v1/ws`.
Полный E2E ассистента также требует отдельный worker, которого нет в указанной
инфраструктуре.

## Delivery / proxy

Для локального запуска используй Vite на `5173`: его proxy направляет `/api` на
backend `8000`. Docker compose frontend не публикует порт на хост, а nginx.conf
не содержит `location /api` с proxy_pass. Поэтому browser E2E сейчас должен идти
через Vite dev server, пока production reverse proxy не будет добавлен.
