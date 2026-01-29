import pytest


@pytest.mark.parametrize(
    ("path", "params"),
    [
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
async def test_agency_geo_endpoints_require_api_key_negative(
    api_client, build_url, path, params
):
    response = await api_client.get(build_url(path), params=params)

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


async def test_list_agencies_by_geo_radius_positive(
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


async def test_list_agencies_by_geo_bbox_positive(
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


@pytest.mark.parametrize(
    "params",
    [
        {"lat": 55.7558, "lon": 37.6173},
        {
            "lat": 55.7558,
            "lon": 37.6173,
            "radius_m": 1000,
            "min_lat": 55.7,
            "max_lat": 55.8,
            "min_lon": 37.5,
            "max_lon": 37.7,
        },
    ],
)
async def test_list_agencies_by_geo_invalid_params_negative(
    api_client, api_headers, build_url, params
):
    response = await api_client.get(
        build_url("/agency/geo"),
        params=params,
        headers=api_headers,
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
