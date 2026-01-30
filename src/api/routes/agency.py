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
    match params:
        case AgencyListQuery(
            building_id=int() as building_id, activity_id=None, name=None
        ):
            rows = await agency_queries.list_agencies_by_building(
                session=session,
                building_id=building_id,
            )
            return [AgencyOut.model_validate(row) for row in rows]
        case AgencyListQuery(
            activity_id=int() as activity_id,
            include_descendants=bool() as include_descendants,
            building_id=None,
            name=None,
        ):
            rows = await agency_queries.list_agencies_by_activity(
                session=session,
                activity_id=activity_id,
                include_descendants=include_descendants,
            )
            return [AgencyOut.model_validate(row) for row in rows]
        case AgencyListQuery(
            name=str() as name, activity_id=None, building_id=None
        ):
            rows = await agency_queries.list_agencies_by_name(
                session=session, name=name
            )
            return [AgencyOut.model_validate(row) for row in rows]
        case _:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specify exactly one filter.",
            )


@router.get("/agency/geo", response_model=list[AgencyOut])
async def list_agencies_by_geo(
    params: Annotated[AgencyGeoQuery, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[AgencyOut]:
    rows = await agency_queries.list_agencies_by_geo(
        session=session, geo=params
    )
    return [AgencyOut.model_validate(row) for row in rows]


@router.get("/agency/{agency_id}", response_model=AgencyOut)
async def get_agency(
    agency_id: Annotated[int, Path(ge=1)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AgencyOut:
    agency = await agency_queries.get_agency_by_id(
        session=session, agency_id=agency_id
    )
    if agency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency not found.",
        )
    return AgencyOut.model_validate(agency)
