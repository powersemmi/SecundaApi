import pytest


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/agency", {"building_id": 1}),
        ("/agency", {"activity_id": 1}),
        ("/agency", {"activity_id": 1, "include_descendants": True}),
        ("/agency", {"name": "Roga i Kopita"}),
    ],
)
async def test_agency_list_endpoints_require_api_key_negative(
    api_client, build_url, path, params
):
    response = await api_client.get(build_url(path), params=params)

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


async def test_list_agencies_by_building_positive(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/agency"),
        params={"building_id": 1},
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())


async def test_list_agencies_by_activity_positive(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/agency"),
        params={"activity_id": 1},
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())


async def test_search_agencies_by_activity_descendants_positive(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/agency"),
        params={"activity_id": 1, "include_descendants": True},
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())


async def test_search_agencies_by_name_positive(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/agency"),
        params={"name": "Roga i Kopita"},
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"building_id": 1, "activity_id": 2},
        {"building_id": 1, "name": "Roga"},
        {"activity_id": 1, "name": "Roga"},
    ],
)
async def test_list_agencies_invalid_filters_negative(
    api_client, api_headers, build_url, params
):
    response = await api_client.get(
        build_url("/agency"),
        params=params,
        headers=api_headers,
    )

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
