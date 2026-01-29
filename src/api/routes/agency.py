from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.queries import agency as agency_queries
from api.dependencies.auth import verify_api_key
from api.dependencies.db import get_session
from api.models.agency import AgencyGeoQuery, AgencyListQuery, AgencyOut

router = APIRouter(
    tags=["agency"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/agency", response_model=list[AgencyOut])
async def list_agencies(
    params: Annotated[AgencyListQuery, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[AgencyOut]:
    filters = [
        params.building_id is not None,
        params.activity_id is not None,
        params.name is not None,
    ]
    if sum(filters) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specify exactly one filter.",
        )

    if params.building_id is not None:
        rows = await agency_queries.list_agencies_by_building(
            session,
            params.building_id,
        )
        return [AgencyOut.model_validate(row) for row in rows]
    if params.activity_id is not None:
        rows = await agency_queries.list_agencies_by_activity(
            session,
            params.activity_id,
            params.include_descendants,
        )
        return [AgencyOut.model_validate(row) for row in rows]
    rows = await agency_queries.list_agencies_by_name(
        session, params.name or ""
    )
    return [AgencyOut.model_validate(row) for row in rows]


@router.get("/agency/geo", response_model=list[AgencyOut])
async def list_agencies_by_geo(
    params: Annotated[AgencyGeoQuery, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[AgencyOut]:
    rows = await agency_queries.list_agencies_by_geo(session, params)
    return [AgencyOut.model_validate(row) for row in rows]


@router.get("/agency/{agency_id}", response_model=AgencyOut)
async def get_agency(
    agency_id: Annotated[int, Path(ge=1)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AgencyOut:
    agency = await agency_queries.get_agency_by_id(session, agency_id)
    if agency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency not found.",
        )
    return AgencyOut.model_validate(agency)
