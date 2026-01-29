set shell := ["sh", "-c"]

postgres:
	docker compose up -d postgres

up:
	docker compose up -d --build

test:
	docker compose run --rm --use-aliases --no-deps backend-test python -m pytest -m "not postgres"

test-all: postgres
	docker compose run --rm --use-aliases --no-deps backend-test python -m pytest

test-postgres: postgres
	docker compose run --rm --use-aliases --no-deps backend-test python -m pytest -m "postgres"

openapi:
	docker compose run --rm --no-deps -v "$(pwd):/work" -w /work -e PYTHONPATH=/work/src backend-test /app/.venv/bin/python -c 'import json; from api.app import create_app; schema=create_app().openapi(); json.dump(schema, open("openapi.yaml","w"), ensure_ascii=False, indent=2)'

down:
	docker compose down -v --remove-orphans
