# Secunda API

backend-сервис на FastAPI + SQLAlchemy (async) с миграциями Alembic.

## Требования

- Docker + Docker Compose
- `just` (опционально, для удобных команд)

## Быстрый запуск

```bash
docker compose up --build
```

После старта доступны:
- API через Nginx: `http://localhost:8080`
- Backend напрямую: `http://localhost:8000/api/v1`
- OpenAPI: `http://localhost:8000/docs`
- Postgres: `localhost:5432`

При запуске `backend` автоматически применяет миграции:
`python -m alembic upgrade head`, затем стартует приложение.
Команда запуска описана в `docker-compose.yaml`.

Остановка и очистка:

```bash
docker compose down
```

Полный запуск через `just` (без dev контейнера):

```bash
just up
```

## Переменные окружения

Основные параметры (см. `src/api/settings.py`):
- `BIND` — адрес и порт приложения, по умолчанию `0.0.0.0:8080`
- `DEBUG` — режим отладки (`True/False`)
- `PG_URL` — строка подключения к Postgres

В `docker-compose.yaml` значения заданы через `environment`.
Убедитесь, что имя БД в `PG_URL` совпадает с `POSTGRES_DB` у сервиса Postgres.

## Тесты (в Docker)

В проекте есть `Justfile` с готовыми командами. Все тесты запускаются в
контейнере `backend-test`, который содержит dev-зависимости.

Unit-тесты (без `postgres`):

```bash
just test
```

Интеграционные тесты (требуют Postgres):

```bash
just test-postgres
```

Все тесты:

```bash
just test-all
```

Остановить и удалить контейнеры и данные:

```bash
just down
```

Если `just` не установлен, используйте прямые команды:

```bash
docker compose up -d postgres
docker compose run --rm --use-aliases --no-deps backend-test python -m pytest -m "postgres"
```

## OpenAPI

Сгенерировать `openapi.yaml` из текущего кода:

```bash
just openapi
```

Файл сохраняется в корне репозитория как `openapi.yaml`.

## Демо-данные

SQL-скрипт добавляет примеры зданий, организаций, телефонов и дерева
деятельностей из задания.

```bash
just seed
```

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
