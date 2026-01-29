from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from api.models.actiivty import ActivityOut
from api.models.building import BuildingOut
from api.models.geo import GeoQueryBase


class AgencyListQuery(BaseModel):
    building_id: Annotated[int | None, Field(default=None, ge=1)]
    activity_id: Annotated[int | None, Field(default=None, ge=1)]
    include_descendants: bool = False
    name: str | None = None


class AgencyGeoQuery(GeoQueryBase):
    pass


class AgencyOut(BaseModel):
    id: int
    name: str
    phones: Annotated[list[str], Field(default_factory=list)]
    building: BuildingOut
    activities: Annotated[list[ActivityOut], Field(default_factory=list)]
