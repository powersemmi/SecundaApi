from __future__ import annotations

from pydantic import BaseModel

from api.models.geo import GeoQueryBase


class BuildingGeoQuery(GeoQueryBase):
    pass


class BuildingOut(BaseModel):
    id: int
    address: str
    lat: float
    lon: float
