FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ python3-dev libc-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

FROM builder AS test

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHON_DISABLE_REMOTE_DEBUG=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

RUN uv sync --frozen --group dev

COPY tests ./tests

FROM python:3.14-slim AS runner

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHON_DISABLE_REMOTE_DEBUG=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY src ./src
COPY alembic.ini .

CMD ["python", "-m", "api"]
