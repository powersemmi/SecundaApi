import pytest


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/agency/1", None),
    ],
)
async def test_agency_get_endpoint_requires_api_key_negative(
    api_client, build_url, path, params
):
    response = await api_client.get(build_url(path), params=params)

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


async def test_get_agency_by_id_positive(
    api_client, api_headers, assert_json_object, build_url
):
    response = await api_client.get(
        build_url("/agency/1"),
        headers=api_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_json_object(response.json())


async def test_get_agency_by_id_not_found_negative(
    api_client, api_headers, build_url
):
    response = await api_client.get(
        build_url("/agency/999"),
        headers=api_headers,
    )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
