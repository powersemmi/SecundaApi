from typing import Any

from sqlalchemy import Select, String, cast, exists, func, literal, select
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement, Subquery

from api.database.queries.geo import apply_geo_filter
from api.database.schema.actiivty import (
    Activity,
    ActivityClosure,
    ActivityName,
    ActivityParent,
)
from api.database.schema.agency import (
    Agency,
    AgencyActivity,
    AgencyBuilding,
    AgencyName,
    AgencyPhone,
)
from api.database.schema.building import (
    Building,
    BuildingAddress,
    BuildingGeo,
)
from api.models.agency import AgencyGeoQuery


def _agency_phones_subquery() -> Subquery:
    return (
        select(
            AgencyPhone.agency_id,
            func.array_agg(AgencyPhone.phone).label("phones"),
        )
        .group_by(AgencyPhone.agency_id)
        .subquery()
    )


def _agency_activities_subquery() -> Subquery:
    return (
        select(
            AgencyActivity.agency_id,
            func.jsonb_agg(
                func.jsonb_build_object(
                    "id",
                    Activity.id,
                    "name",
                    ActivityName.name,
                    "parent_id",
                    ActivityParent.parent_id,
                )
            ).label("activities"),
        )
        .join(Activity, Activity.id == AgencyActivity.activity_id)
        .join(ActivityName, ActivityName.activity_id == Activity.id)
        .outerjoin(ActivityParent, ActivityParent.activity_id == Activity.id)
        .group_by(AgencyActivity.agency_id)
        .subquery()
    )


def _agency_select() -> Select[Any]:
    phones = _agency_phones_subquery()
    activities = _agency_activities_subquery()
    empty_phones = cast(literal("{}"), ARRAY(String))
    empty_activities = cast(literal("[]"), JSONB)

    return (
        select(
            Agency.id.label("id"),
            AgencyName.name.label("name"),
            func.coalesce(phones.c.phones, empty_phones).label("phones"),
            func.jsonb_build_object(
                "id",
                Building.id,
                "address",
                BuildingAddress.address,
                "lat",
                func.ST_Y(BuildingGeo.geom),
                "lon",
                func.ST_X(BuildingGeo.geom),
            ).label("building"),
            func.coalesce(activities.c.activities, empty_activities).label(
                "activities"
            ),
        )
        .join(AgencyName, AgencyName.agency_id == Agency.id)
        .join(AgencyBuilding, AgencyBuilding.agency_id == Agency.id)
        .join(Building, Building.id == AgencyBuilding.building_id)
        .join(BuildingAddress, BuildingAddress.building_id == Building.id)
        .join(BuildingGeo, BuildingGeo.building_id == Building.id)
        .outerjoin(phones, phones.c.agency_id == Agency.id)
        .outerjoin(activities, activities.c.agency_id == Agency.id)
    )


def _activity_filter(
    activity_id: int,
    include_descendants: bool,
) -> ColumnElement[bool]:
    stmt = select(1).select_from(AgencyActivity)
    stmt = stmt.where(AgencyActivity.agency_id == Agency.id)
    if include_descendants:
        stmt = stmt.join(
            ActivityClosure,
            ActivityClosure.descendant_id == AgencyActivity.activity_id,
        ).where(ActivityClosure.ancestor_id == activity_id)
    else:
        stmt = stmt.where(AgencyActivity.activity_id == activity_id)
    return exists(stmt)


async def list_agencies_by_building(
    session: AsyncSession,
    building_id: int,
) -> list[dict[str, Any]]:
    stmt = _agency_select().where(AgencyBuilding.building_id == building_id)
    result = await session.execute(stmt)
    return [dict(row) for row in result.mappings().all()]


async def list_agencies_by_activity(
    session: AsyncSession,
    activity_id: int,
    include_descendants: bool,
) -> list[dict[str, Any]]:
    stmt = _agency_select().where(
        _activity_filter(activity_id, include_descendants)
    )
    result = await session.execute(stmt)
    return [dict(row) for row in result.mappings().all()]


async def list_agencies_by_geo(
    session: AsyncSession,
    geo: AgencyGeoQuery,
) -> list[dict[str, Any]]:
    stmt = _agency_select()
    stmt = apply_geo_filter(stmt, geo, BuildingGeo.geom)
    result = await session.execute(stmt)
    return [dict(row) for row in result.mappings().all()]


async def list_agencies_by_name(
    session: AsyncSession,
    name: str,
) -> list[dict[str, Any]]:
    stmt = _agency_select().where(AgencyName.name.ilike(f"%{name}%"))
    result = await session.execute(stmt)
    return [dict(row) for row in result.mappings().all()]


async def get_agency_by_id(
    session: AsyncSession,
    agency_id: int,
) -> dict[str, Any] | None:
    stmt = _agency_select().where(Agency.id == agency_id)
    result = await session.execute(stmt)
    row = result.mappings().one_or_none()
    return dict(row) if row else None
