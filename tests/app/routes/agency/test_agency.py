import pytest


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/agency", {"building_id": 1}),
        ("/agency", {"activity_id": 1}),
        ("/agency", {"activity_id": 1, "include_descendants": True}),
        ("/agency", {"name": "Roga i Kopita"}),
        ("/agency/1", None),
        (
            "/agency/geo",
            {
                "lat": 55.7558,
                "lon": 37.6173,
                "radius_m": 1000,
            },
        ),
        (
            "/agency/geo",
            {
                "min_lat": 55.7,
                "max_lat": 55.8,
                "min_lon": 37.5,
                "max_lon": 37.7,
            },
        ),
    ],
)
async def test_agency_endpoints_require_api_key(
    api_client, build_url, path, params
):
    response = await api_client.get(build_url(path), params=params)

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


async def test_list_agencies_by_building_returns_json_list(
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


async def test_list_agencies_by_activity_returns_json_list(
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


async def test_search_agencies_by_activity_descendants_returns_json_list(
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


async def test_search_agencies_by_name_returns_json_list(
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


async def test_get_agency_by_id_returns_json_object(
    api_client, api_headers, assert_json_object, build_url
):
    response = await api_client.get(
        build_url("/agency/1"),
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_object(response.json())


async def test_list_agencies_by_geo_radius_returns_json_list(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/agency/geo"),
        params={"lat": 55.7558, "lon": 37.6173, "radius_m": 1000},
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())


async def test_list_agencies_by_geo_bbox_returns_json_list(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/agency/geo"),
        params={
            "min_lat": 55.7,
            "max_lat": 55.8,
            "min_lon": 37.5,
            "max_lon": 37.7,
        },
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())
