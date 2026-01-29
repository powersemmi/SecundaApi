import pytest

from api.database.queries.agency import list_agencies_by_name
from tests.app.database.queries.conftest import (
    create_agency,
    create_building,
)

pytestmark = pytest.mark.postgres


async def test_list_agencies_by_name_positive(db_session):
    building = await create_building(
        db_session,
        address="Name Address",
        lat=55.0,
        lon=37.0,
    )
    await create_agency(
        db_session,
        name="Roga i Kopita",
        building=building,
    )
    await create_agency(
        db_session,
        name="Other",
        building=building,
    )

    result = await list_agencies_by_name(db_session, "Roga")

    assert len(result) == 1
    assert result[0]["name"] == "Roga i Kopita"


async def test_list_agencies_by_name_negative(db_session):
    building = await create_building(
        db_session,
        address="Empty Address",
        lat=55.0,
        lon=37.0,
    )
    await create_agency(
        db_session,
        name="Other",
        building=building,
    )

    result = await list_agencies_by_name(db_session, "Missing")

    assert result == []
