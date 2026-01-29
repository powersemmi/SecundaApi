import pytest


@pytest.mark.parametrize(
    ("path", "params"),
    [
        (
            "/building/geo",
            {"lat": 55.7558, "lon": 37.6173, "radius_m": 1000},
        ),
        (
            "/building/geo",
            {
                "min_lat": 55.7,
                "max_lat": 55.8,
                "min_lon": 37.5,
                "max_lon": 37.7,
            },
        ),
    ],
)
async def test_building_endpoints_require_api_key(
    api_client, build_url, path, params
):
    response = await api_client.get(build_url(path), params=params)

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


async def test_list_buildings_by_geo_radius_returns_json_list(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/building/geo"),
        params={"lat": 55.7558, "lon": 37.6173, "radius_m": 1000},
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_list(response.json())


async def test_list_buildings_by_geo_bbox_returns_json_list(
    api_client, api_headers, assert_json_list, build_url
):
    response = await api_client.get(
        build_url("/building/geo"),
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
