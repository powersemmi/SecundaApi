import pytest


async def test_activity_endpoint_requires_api_key(api_client, build_url):
    response = await api_client.post(
        build_url("/activity"),
        json={"name": "Food", "parent_id": None},
    )

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.parametrize(
    ("depth", "expected_status"),
    [
        (1, 201),
        (2, 201),
        (3, 201),
        (4, 400),
    ],
)
async def test_activity_depth_limit_3(
    api_client, api_headers, build_url, depth, expected_status
):
    base_url = build_url("/activity")

    parent_id = None
    for level in range(1, depth + 1):
        response = await api_client.post(
            base_url,
            json={"name": f"Level {level}", "parent_id": parent_id},
            headers=api_headers,
        )
        if level == depth:
            assert response.status_code == expected_status
            assert response.headers["content-type"].startswith(
                "application/json"
            )
        else:
            assert response.status_code == 201
            parent_id = response.json()["id"]
