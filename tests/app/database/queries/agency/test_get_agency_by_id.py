import pytest

from api.database.queries.agency import get_agency_by_id
from tests.app.database.queries.conftest import (
    create_agency,
    create_building,
)

pytestmark = pytest.mark.postgres


async def test_get_agency_by_id_positive(db_session):
    building = await create_building(
        db_session,
        address="Get Address",
        lat=55.0,
        lon=37.0,
    )
    agency = await create_agency(
        db_session,
        name="Find Me",
        building=building,
    )

    found = await get_agency_by_id(db_session, agency.id)

    assert found is not None
    assert found["id"] == agency.id
    assert found["name"] == "Find Me"


async def test_get_agency_by_id_negative(db_session):
    building = await create_building(
        db_session,
        address="Missing Address",
        lat=55.0,
        lon=37.0,
    )
    agency = await create_agency(
        db_session,
        name="Missing",
        building=building,
    )

    missing = await get_agency_by_id(db_session, agency.id + 1)

    assert missing is None
