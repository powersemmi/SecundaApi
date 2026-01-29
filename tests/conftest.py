from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from api.app import create_app
from api.settings import settings

API_KEY_HEADER = "X-API-Key"
API_KEY_VALUE = "test-api-key"


@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, Any]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def api_headers() -> dict[str, str]:
    return {API_KEY_HEADER: API_KEY_VALUE}


@pytest.fixture(scope="session")
def api_base_path() -> str:
    return settings.ROOT_PATH.rstrip("/")


@pytest.fixture
def build_url(api_base_path: str):
    def _build(path: str) -> str:
        if not api_base_path:
            return path
        return f"{api_base_path}{path}"

    return _build


@pytest.fixture
def assert_json_list():
    def _assert(payload: Any) -> None:
        assert isinstance(payload, list)

    return _assert


@pytest.fixture
def assert_json_object():
    def _assert(payload: Any) -> None:
        assert isinstance(payload, dict)

    return _assert
