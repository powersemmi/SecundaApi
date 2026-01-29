import pytest

from api.database.queries.agency import list_agencies_by_building
from tests.app.database.queries.conftest import (
    create_agency,
    create_building,
)

pytestmark = pytest.mark.postgres


async def test_list_agencies_by_building_positive(db_session):
    building = await create_building(
        db_session,
        address="Test Address",
        lat=55.0,
        lon=37.0,
    )
    agency = await create_agency(
        db_session,
        name="Roga i Kopita",
        building=building,
        phones=["111-111"],
    )

    result = await list_agencies_by_building(db_session, building.id)

    assert len(result) == 1
    row = result[0]
    assert row["id"] == agency.id
    assert row["name"] == "Roga i Kopita"
    assert row["building"]["id"] == building.id
    assert list(row["phones"]) == ["111-111"]
    assert row["activities"] == []


async def test_list_agencies_by_building_negative(db_session):
    building = await create_building(
        db_session,
        address="Empty Address",
        lat=55.0,
        lon=37.0,
    )

    result = await list_agencies_by_building(db_session, building.id)

    assert result == []
