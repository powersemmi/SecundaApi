from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import Select, cast, func
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

from api.models.geo import GeoQueryBase


def apply_geo_filter(
    stmt: Select[Any],
    geo: GeoQueryBase,
    geom_col: ColumnElement[Any] | InstrumentedAttribute[Any],
) -> Select[Any]:
    if (
        geo.radius_m is not None
        and geo.lat is not None
        and geo.lon is not None
    ):
        point = func.ST_SetSRID(func.ST_MakePoint(geo.lon, geo.lat), 4326)
        return stmt.where(
            func.ST_DWithin(
                cast(geom_col, Geography),
                cast(point, Geography),
                geo.radius_m,
            )
        )
    if (
        geo.min_lat is None
        or geo.max_lat is None
        or geo.min_lon is None
        or geo.max_lon is None
    ):
        raise ValueError("Bounding box parameters are required.")
    envelope = func.ST_MakeEnvelope(
        geo.min_lon,
        geo.min_lat,
        geo.max_lon,
        geo.max_lat,
        4326,
    )
    return stmt.where(func.ST_Intersects(geom_col, envelope))
