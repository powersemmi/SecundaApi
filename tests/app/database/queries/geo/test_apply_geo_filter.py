import pytest
from sqlalchemy import select

from api.database.queries.geo import apply_geo_filter
from api.database.schema.building import Building, BuildingGeo
from api.models.building import BuildingGeoQuery
from tests.app.database.queries.conftest import create_building

pytestmark = pytest.mark.postgres


async def test_apply_geo_filter_radius_positive(db_session):
    near = await create_building(
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

    stmt = select(Building.id).join(
        BuildingGeo, BuildingGeo.building_id == Building.id
    )
    geo = BuildingGeoQuery(lat=55.0, lon=37.0, radius_m=2000)
    stmt = apply_geo_filter(stmt, geo, BuildingGeo.geom)
    result = await db_session.execute(stmt)

    assert result.scalars().all() == [near.id]


async def test_apply_geo_filter_bbox_positive(db_session):
    inside = await create_building(
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

    stmt = select(Building.id).join(
        BuildingGeo, BuildingGeo.building_id == Building.id
    )
    geo = BuildingGeoQuery(
        min_lat=55.0,
        max_lat=55.2,
        min_lon=37.0,
        max_lon=37.2,
    )
    stmt = apply_geo_filter(stmt, geo, BuildingGeo.geom)
    result = await db_session.execute(stmt)

    assert result.scalars().all() == [inside.id]


def test_building_geo_query_requires_complete_radius_negative():
    with pytest.raises(
        ValueError, match="lat, lon, and radius_m must be provided together"
    ):
        BuildingGeoQuery(lat=55.0, lon=37.0)


def test_building_geo_query_disallows_mixed_shapes_negative():
    with pytest.raises(
        ValueError,
        match="Specify either radius search or bounding box, not both",
    ):
        BuildingGeoQuery(
            lat=55.0,
            lon=37.0,
            radius_m=1000,
            min_lat=55.0,
            max_lat=55.2,
            min_lon=37.0,
            max_lon=37.2,
        )
