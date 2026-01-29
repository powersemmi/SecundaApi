# Secunda API

Минимальный backend-сервис на FastAPI + SQLAlchemy (async) с миграциями Alembic.

## Быстрый запуск через Docker Compose

```bash
docker compose up --build
```

После старта доступны:
- API через Nginx: `http://localhost:8080`
- Backend напрямую: `http://localhost:8000/api/v1`
- OpenApi: `http://localhost:8000/docs`
- Postgres: `localhost:5432`

При запуске `backend` автоматически применяет миграции:
`python -m alembic upgrade head`, затем стартует приложение.
Команда запуска описана в `docker-compose.yaml`.

Остановка и очистка:

```bash
docker compose down
```

## Переменные окружения

Основные параметры (см. `src/api/settings.py`):
- `BIND` — адрес и порт приложения, по умолчанию `0.0.0.0:8080`
- `DEBUG` — режим отладки (`True/False`)
- `PG_URL` — строка подключения к Postgres

В `docker-compose.yaml` значения заданы через `environment`.
Убедитесь, что имя БД в `PG_URL` совпадает с `POSTGRES_DB` у сервиса Postgres.

## Структура проекта

- `src/api` — исходники приложения
- `src/api/database/schema` — ORM-модели SQLAlchemy
- `src/api/migration` — Alembic
- `docker-compose.yaml` — локальная инфраструктура (Postgres, backend, nginx)
- `.conf/` — конфиги Postgres и Nginx

## Локальный запуск без Docker (опционально)

Проект использует `uv` для установки зависимостей.
Настройте `PG_URL` в `.env`, затем используйте ту же команду старта,
что и в `docker-compose.yaml`.
