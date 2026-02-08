# Запуск в Docker

У каждого контейнера свой набор зависимостей и только нужный код (api — без ultralytics/streamlit, worker — без fastapi/streamlit, frontend — только streamlit и requests).

Из **корня проекта**:

```bash
docker compose up -d --build
```

- **API:** http://localhost:8000  
- **Frontend (UI):** http://localhost:8501  
- **Redis:** localhost:6379 (внутри сети — `redis:6379`)

Остановка:

```bash
docker compose down
```

## Тома и модели

- **media** — общий том для входных и выходных снимков (api и worker).
- **Модели** — каталог `backend/worker/models` с хоста монтируется в worker как `/models`. Положите туда свои `.pt` (например `yolo11s_bf.pt`, `rtdetr-bf.pt`) до запуска или перезапустите после добавления: `docker compose up -d worker`.

## Переменные окружения

При необходимости задайте в `docker-compose.yml` или через `.env`:

- `MEDIA_ROOT` — в api и worker уже `/media`.
- `CELERY_BROKER_URL` — по умолчанию `redis://redis:6379/0`.
- `BACKEND_URL` — во frontend по умолчанию `http://api:8000` (для запросов из контейнера).
