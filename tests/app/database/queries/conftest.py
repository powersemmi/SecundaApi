from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from api.database.schema.actiivty import Activity
from api.database.schema.agency import (
    Agency,
    AgencyActivity,
    AgencyBuilding,
    AgencyName,
    AgencyPhone,
)
from api.database.schema.base import metadata
from api.database.schema.building import Building, BuildingAddress, BuildingGeo
from api.settings import settings


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        settings.PG_URL.unicode_string(),
        echo=False,
        pool_pre_ping=True,
    )
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(
    db_engine,
) -> AsyncGenerator[AsyncSession]:
    async with db_engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


async def create_building(
    session: AsyncSession,
    address: str,
    lat: float,
    lon: float,
) -> Building:
    building = await Building.create(session)
    await BuildingAddress.create(
        session,
        building_id=building.id,
        address=address,
    )
    await BuildingGeo.create(
        session,
        building_id=building.id,
        lat=lat,
        lon=lon,
    )
    return building


async def create_agency(
    session: AsyncSession,
    name: str,
    building: Building,
    phones: list[str] | None = None,
    activity_ids: list[int] | None = None,
) -> Agency:
    agency = await Agency.create(session)
    await AgencyName.create(session, agency_id=agency.id, name=name)
    await AgencyBuilding.create(
        session,
        agency_id=agency.id,
        building_id=building.id,
    )
    for phone in phones or []:
        await AgencyPhone.create(session, agency_id=agency.id, phone=phone)
    for activity_id in activity_ids or []:
        await AgencyActivity.create(
            session,
            agency_id=agency.id,
            activity_id=activity_id,
        )
    return agency


async def create_activity(
    session: AsyncSession,
    name: str,
    parent_id: int | None,
) -> Activity:
    return await Activity.create_activity(
        session,
        name=name,
        parent_id=parent_id,
    )
