from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.queries import building as building_queries
from api.dependencies.auth import verify_api_key
from api.dependencies.db import get_session
from api.models.building import BuildingGeoQuery, BuildingOut

router = APIRouter(
    tags=["building"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/building/geo", response_model=list[BuildingOut])
async def list_buildings_by_geo(
    params: Annotated[BuildingGeoQuery, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[BuildingOut]:
    rows = await building_queries.list_buildings_by_geo(session, params)
    return [BuildingOut.model_validate(row) for row in rows]
