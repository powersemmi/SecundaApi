import pytest

from api.database.queries.building import list_buildings_by_geo
from api.models.building import BuildingGeoQuery
from tests.app.database.queries.conftest import create_building

pytestmark = pytest.mark.postgres


async def test_list_buildings_by_geo_radius_positive(db_session):
    await create_building(
        db_session,
        address="Near",
        lat=55.0,
        lon=37.0,
    )
    await create_building(
        db_session,
        address="Far",
        lat=56.0,
        lon=37.0,
    )

    geo = BuildingGeoQuery(lat=55.0, lon=37.0, radius_m=2000)
    result = await list_buildings_by_geo(db_session, geo)

    assert len(result) == 1
    assert result[0]["address"] == "Near"


async def test_list_buildings_by_geo_bbox_positive(db_session):
    await create_building(
        db_session,
        address="Inside",
        lat=55.1,
        lon=37.1,
    )
    await create_building(
        db_session,
        address="Outside",
        lat=56.0,
        lon=37.0,
    )

    geo = BuildingGeoQuery(
        min_lat=55.0,
        max_lat=55.2,
        min_lon=37.0,
        max_lon=37.2,
    )
    result = await list_buildings_by_geo(db_session, geo)

    assert len(result) == 1
    assert result[0]["address"] == "Inside"


async def test_list_buildings_by_geo_radius_negative(db_session):
    await create_building(
        db_session,
        address="Far",
        lat=56.0,
        lon=37.0,
    )

    geo = BuildingGeoQuery(lat=55.0, lon=37.0, radius_m=2000)
    result = await list_buildings_by_geo(db_session, geo)

    assert result == []
