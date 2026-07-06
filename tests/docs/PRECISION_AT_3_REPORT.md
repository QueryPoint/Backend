# Отчёт: Precision@3 (QA-05)

## Условия прогона

- Стенд: локальный docker-compose (`Infra/docker-compose.yml` — Postgres, Redis, Elasticsearch, MinIO, RabbitMQ) + backend, запущенный локально против него.
- Данные: 10 реальных PDF-документов, загруженных через `Infra/init.sh` (DO-07) — статьи arXiv (`lecture_1.pdf` … `lecture_10.pdf`, в порядке загрузки соответствуют arXiv ID из `init.sh`).
- Пользователь: `init_seed_user`, поиск выполнялся через реальный `GET /api/v1/search?q=...&limit=3`.
- Дата прогона: 06.07.2026.

## Методика

Для каждого документа сформирован один эталонный запрос на основе его содержания (без использования точного заголовка статьи, чтобы проверить полнотекстовый, а не keyword-match поиск). Успех — ожидаемый документ присутствует среди первых 3 результатов (`limit=3`).

## Результаты

| № | Запрос | Ожидаемый документ | Топ-3 результата (файл — score) | В топ-3? |
|---|---|---|---|---|
| 1 | self-attention Transformer | lecture_1.pdf | lecture_1.pdf (15.90), lecture_1.pdf (11.07), lecture_2.pdf (10.65) | ✅ (1-е место) |
| 2 | bidirectional encoder representations | lecture_2.pdf | lecture_2.pdf (13.24), lecture_2.pdf (8.60), lecture_2.pdf (8.08) | ✅ (1-е место) |
| 3 | residual learning deep networks | lecture_3.pdf | lecture_3.pdf (13.96), lecture_1.pdf (13.52), lecture_3.pdf (10.18) | ✅ (1-е место) |
| 4 | very deep convolutional networks | lecture_4.pdf | lecture_4.pdf (12.42), lecture_4.pdf (11.19), lecture_3.pdf (11.09) | ✅ (1-е место) |
| 5 | generative adversarial networks | lecture_5.pdf | lecture_5.pdf (10.71), lecture_5.pdf (10.11), lecture_5.pdf (6.93) | ✅ (1-е место) |
| 6 | few-shot learning language models | lecture_6.pdf | lecture_6.pdf (14.57), lecture_6.pdf (12.87), lecture_6.pdf (12.63) | ✅ (1-е место) |
| 7 | vector representations of words | lecture_7.pdf | lecture_7.pdf (11.74), lecture_7.pdf (9.28), lecture_7.pdf (9.17) | ✅ (1-е место) |
| 8 | knowledge distillation neural network | lecture_8.pdf | lecture_8.pdf (12.17), lecture_8.pdf (10.42), lecture_9.pdf (7.72) | ✅ (1-е место) |
| 9 | neural machine translation align translate | lecture_9.pdf | lecture_9.pdf (25.32), lecture_9.pdf (14.06), lecture_9.pdf (12.75) | ✅ (1-е место) |
| 10 | stochastic optimization Adam | lecture_10.pdf | lecture_10.pdf (15.59), lecture_10.pdf (10.28), lecture_10.pdf (9.59) | ✅ (1-е место) |

## Итог

**Precision@3 = 10 / 10 = 100%**

Все 10 эталонных запросов вернули ожидаемый документ, причём во всех случаях — на первом месте выдачи. Повторяющиеся вхождения одного файла в топ-3 (разные чанки/страницы одного документа) не мешают метрике — оценивается факт присутствия документа, а не уникальность позиций.

Ограничение методики: запросы и документы — на английском (реальные arXiv-статьи), а маппинг Elasticsearch использует `russian` analyzer (см. `src/core/elasticsearch/es_servise.py`). Результат показывает, что базовая токенизация работает достаточно хорошо и для английского текста, но качество полнотекстового поиска по русскоязычным документам может отличаться — это стоит перепроверить отдельно на реальных русскоязычных лекциях перед продакшен-использованием.
