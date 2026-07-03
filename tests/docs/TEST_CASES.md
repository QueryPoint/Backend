# Набор тест-кейсов

| ID | Сценарий | Действие | Ожидаемый результат |
|---|---|---|---|
| AUTH-01 | Регистрация | Валидный username и пароль | `201`, объект пользователя |
| AUTH-02 | Username граница | 2 / 3 / 25 / 26 символов | 2 и 26 отклоняются, 3 и 25 принимаются |
| AUTH-03 | Username символы | кириллица, пробел, дефис, email, цифра первым символом | `422` |
| AUTH-04 | Login | верный/неверный пароль | `200` + cookies / `401` |
| AUTH-05 | Refresh | отсутствующий, испорченный, истёкший token | `401` |
| DOC-01 | Upload PDF | валидный PDF | `201`, `status=uploaded` |
| DOC-02 | Upload DOCX | валидный DOCX | `201`, `status=uploaded` |
| DOC-03 | Размер | >20 MB | `400` в текущей реализации (`Invalid document`) |
| DOC-04 | MIME | TXT/JPG/ZIP/поддельный PDF | `400` |
| DOC-05 | Изоляция | запросить чужой документ | `403` |
| DOC-06 | Удаление | удалить существующий/несуществующий | `204` / `404` |
| SEARCH-01 | Поиск | существующий запрос | список фрагментов |
| SEARCH-02 | Cache | повторить запрос | ответ из Redis, ES не вызывается |
| SEARCH-03 | Изоляция | разные пользователи | key и ES filter содержат user_id |
| WS-01 | Подключение | без/с access cookie | close `1008` / accepted |
| WS-02 | Prompt | второй prompt во время processing | error `Prompt already processing` |
| WS-03 | Delete | delete message | status `idle`, publish delete |
