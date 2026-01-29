import pytest

from api.database.queries.agency import list_agencies_by_activity
from tests.app.database.queries.conftest import (
    create_activity,
    create_agency,
    create_building,
)

pytestmark = pytest.mark.postgres


async def test_list_agencies_by_activity_with_descendants_positive(
    db_session,
):
    building = await create_building(
        db_session,
        address="Activity Address",
        lat=55.0,
        lon=37.0,
    )
    root = await create_activity(db_session, name="Food", parent_id=None)
    child = await create_activity(db_session, name="Meat", parent_id=root.id)
    agency = await create_agency(
        db_session,
        name="Butcher",
        building=building,
        activity_ids=[child.id],
    )

    result = await list_agencies_by_activity(
        db_session,
        activity_id=root.id,
        include_descendants=True,
    )

    assert [row["id"] for row in result] == [agency.id]


async def test_list_agencies_by_activity_without_descendants_negative(
    db_session,
):
    building = await create_building(
        db_session,
        address="No Desc",
        lat=55.0,
        lon=37.0,
    )
    root = await create_activity(db_session, name="Food", parent_id=None)
    child = await create_activity(db_session, name="Milk", parent_id=root.id)
    await create_agency(
        db_session,
        name="Dairy",
        building=building,
        activity_ids=[child.id],
    )

    result = await list_agencies_by_activity(
        db_session,
        activity_id=root.id,
        include_descendants=False,
    )

    assert result == []
