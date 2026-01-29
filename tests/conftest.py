from collections.abc import AsyncGenerator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.app import create_app
from api.database.queries import agency as agency_queries
from api.database.queries import building as building_queries
from api.database.schema.actiivty import Activity
from api.settings import settings

API_KEY_HEADER = "X-API-Key"
API_KEY_VALUE = "test-api-key"

AGENCY_SAMPLE = {
    "id": 1,
    "name": "Test Agency",
    "phones": [],
    "building": {"id": 1, "address": "Test Address", "lat": 55.0, "lon": 37.0},
    "activities": [],
}


def _should_skip_query_mocks(request: pytest.FixtureRequest) -> bool:
    return bool(request.node.get_closest_marker("postgres"))


async def _get_agency_by_id(
    *args: Any, **kwargs: Any
) -> dict[str, Any] | None:
    agency_id = kwargs.get("agency_id")
    if agency_id is None and len(args) >= 2:
        agency_id = args[1]
    if agency_id == 1:
        return AGENCY_SAMPLE
    return None


def _install_query_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        agency_queries, "list_agencies_by_building", AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        agency_queries, "list_agencies_by_activity", AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        agency_queries, "list_agencies_by_geo", AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        agency_queries, "list_agencies_by_name", AsyncMock(return_value=[])
    )
    monkeypatch.setattr(agency_queries, "get_agency_by_id", _get_agency_by_id)
    monkeypatch.setattr(
        building_queries,
        "list_buildings_by_geo",
        AsyncMock(return_value=[]),
    )


def _install_activity_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = 0

    async def _create_activity(
        cls: type[Activity],
        session: Any,
        name: str,
        parent_id: int | None,
    ) -> Any:
        nonlocal call_count
        call_count += 1
        if call_count > 3:
            raise ValueError("Activity depth limit exceeded.")
        return SimpleNamespace(id=call_count)

    monkeypatch.setattr(
        Activity, "create_activity", classmethod(_create_activity)
    )


@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, Any]:
    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client


@pytest.fixture(autouse=True)
def mock_queries(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    if _should_skip_query_mocks(request):
        return
    _install_query_mocks(monkeypatch)
    _install_activity_mock(monkeypatch)


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
