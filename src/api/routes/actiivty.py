from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.schema.actiivty import Activity
from api.dependencies.auth import verify_api_key
from api.dependencies.db import get_session
from api.models.actiivty import ActivityCreate, ActivityOut

router = APIRouter(
    tags=["activity"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/activity", status_code=201, response_model=ActivityOut)
async def create_activity(
    payload: Annotated[ActivityCreate, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ActivityOut:
    try:
        activity = await Activity.create_activity(
            session,
            name=payload.name,
            parent_id=payload.parent_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ActivityOut(
        id=activity.id,
        name=payload.name,
        parent_id=payload.parent_id,
    )
