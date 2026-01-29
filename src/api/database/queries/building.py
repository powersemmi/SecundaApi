from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.queries.geo import apply_geo_filter
from api.database.schema.building import Building, BuildingAddress, BuildingGeo
from api.models.building import BuildingGeoQuery


def _building_select() -> Select[Any]:
    return (
        select(
            Building.id.label("id"),
            BuildingAddress.address.label("address"),
            func.ST_Y(BuildingGeo.geom).label("lat"),
            func.ST_X(BuildingGeo.geom).label("lon"),
        )
        .join(BuildingAddress, BuildingAddress.building_id == Building.id)
        .join(BuildingGeo, BuildingGeo.building_id == Building.id)
    )


async def list_buildings_by_geo(
    session: AsyncSession,
    geo: BuildingGeoQuery,
) -> list[dict[str, Any]]:
    stmt = _building_select()
    stmt = apply_geo_filter(stmt, geo, BuildingGeo.geom)
    result = await session.execute(stmt)
    return [dict(row) for row in result.mappings().all()]
