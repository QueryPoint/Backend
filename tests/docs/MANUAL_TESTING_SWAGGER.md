# Ручное тестирование через Swagger

Swagger обычно доступен по `http://localhost:8000/docs`. Для защищённых ручек сначала нужно выполнить `POST /api/v1/login`: Swagger/браузер сохранит cookie.

## 1. Проверить, что backend жив
1. Открой `GET /`.
2. Нажми **Try it out** → **Execute**.
3. Ожидается `200` и тело `{"ping":"pong"}`.

## 2. Регистрация
`POST /api/v1/registration`:
```json
{"username":"student_2026","password":"123456"}
```
Ожидается `201` и `user_id`, `username`.

Проверить ошибки: `ab`, `1student`, `иван`, `ivan petrov`, `ivan-petrov`, `ivan@gmail.com`, пароль `12345`. Ожидается `422`. Повторная регистрация — `400 Username already taken`.

## 3. Вход/сессия
`POST /api/v1/login` с корректными данными: `200`, в `Set-Cookie` должны быть `access_token`, `refresh_token`, `HttpOnly`, `SameSite=lax`. Неверный пароль: `401`.

`GET /api/v1/me`: после login `200`; без cookie или с испорченной cookie — `401`.

`POST /api/v1/refresh`: с refresh-cookie `200 {"status":"session_refreshed"}`; без cookie — `401`.

`POST /api/v1/logout`: `200 {"status":"logged_out"}`; после этого `/me` должен вернуть `401`.

## 4. Документы
`POST /api/v1/documents/upload`: выбери поле `file`, передай валидный PDF/DOCX. Ожидается `201 {"status":"uploaded","doc_id":"..."}`.

Проверки: TXT/JPG, пустой файл, >20MB, повреждённый PDF/DOCX. В текущем backend ожидается `400 Invalid document` для неподдерживаемого MIME/размера; ошибки парсинга/S3/ES могут дать `500`.

`GET /api/v1/documents` — `200` список. `GET /api/v1/documents/{doc_id}` — детали и временная ссылка. Чужой document id — `403`; несуществующий — `404`. `DELETE` существующего — `204`.

## 5. Поиск
`GET /api/v1/search?q=<фраза>`: ожидается `200` и список `{file_name,page_number,chunk_id,text,score}`. Повтори одинаковый запрос: ответ должен остаться тем же; Redis должен содержать cache-key. Текущий backend принимает пустую строку `q=` — это зафиксированное ограничение, которое стоит оформить как дефект, если по ТЗ пустой запрос запрещён.

## 6. WebSocket
Swagger не всегда удобен для WebSocket. Используй Postman/Insomnia или браузерный frontend. Без access cookie ожидается закрытие с кодом `1008`. После подключения отправь:
```json
{"type":"prompt","prompt":"Объясни SQL","doc":null}
```
Повторно отправь prompt до ответа: ожидается `{"type":"error","data":"Prompt already processing"}`.
