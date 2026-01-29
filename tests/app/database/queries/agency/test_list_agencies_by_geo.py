import pytest

from api.database.queries.agency import list_agencies_by_geo
from api.models.agency import AgencyGeoQuery
from tests.app.database.queries.conftest import (
    create_agency,
    create_building,
)

pytestmark = pytest.mark.postgres


async def test_list_agencies_by_geo_radius_positive(db_session):
    center = await create_building(
        db_session,
        address="Near",
        lat=55.0,
        lon=37.0,
    )
    far = await create_building(
        db_session,
        address="Far",
        lat=56.0,
        lon=37.0,
    )
    await create_agency(
        db_session,
        name="Near Agency",
        building=center,
    )
    await create_agency(
        db_session,
        name="Far Agency",
        building=far,
    )

    geo = AgencyGeoQuery(lat=55.0, lon=37.0, radius_m=2000)
    result = await list_agencies_by_geo(db_session, geo)

    assert len(result) == 1
    assert result[0]["building"]["address"] == "Near"


async def test_list_agencies_by_geo_bbox_positive(db_session):
    inside = await create_building(
        db_session,
        address="Inside",
        lat=55.1,
        lon=37.1,
    )
    outside = await create_building(
        db_session,
        address="Outside",
        lat=56.0,
        lon=37.0,
    )
    await create_agency(
        db_session,
        name="Inside Agency",
        building=inside,
    )
    await create_agency(
        db_session,
        name="Outside Agency",
        building=outside,
    )

    geo = AgencyGeoQuery(
        min_lat=55.0,
        max_lat=55.2,
        min_lon=37.0,
        max_lon=37.2,
    )
    result = await list_agencies_by_geo(db_session, geo)

    assert len(result) == 1
    assert result[0]["building"]["address"] == "Inside"


async def test_list_agencies_by_geo_radius_negative(db_session):
    far = await create_building(
        db_session,
        address="Far",
        lat=56.0,
        lon=37.0,
    )
    await create_agency(
        db_session,
        name="Far Agency",
        building=far,
    )

    geo = AgencyGeoQuery(lat=55.0, lon=37.0, radius_m=2000)
    result = await list_agencies_by_geo(db_session, geo)

    assert result == []
