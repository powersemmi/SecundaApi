from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class GeoQueryBase(BaseModel):
    lat: Annotated[float | None, Field(ge=-90, le=90)] = None
    lon: Annotated[float | None, Field(ge=-180, le=180)] = None
    radius_m: Annotated[float | None, Field(gt=0)] = None
    min_lat: Annotated[float | None, Field(ge=-90, le=90)] = None
    max_lat: Annotated[float | None, Field(ge=-90, le=90)] = None
    min_lon: Annotated[float | None, Field(ge=-180, le=180)] = None
    max_lon: Annotated[float | None, Field(ge=-180, le=180)] = None

    def _has_any(self, values: tuple[float | None, ...]) -> bool:
        return any(value is not None for value in values)

    def _has_all(self, values: tuple[float | None, ...]) -> bool:
        return all(value is not None for value in values)

    def _validate_bounds(self) -> None:
        if self.min_lat is None or self.max_lat is None:
            raise ValueError("min_lat and max_lat must be provided together.")
        if self.min_lon is None or self.max_lon is None:
            raise ValueError("min_lon and max_lon must be provided together.")
        if self.min_lat > self.max_lat:
            raise ValueError("min_lat must be <= max_lat.")
        if self.min_lon > self.max_lon:
            raise ValueError("min_lon must be <= max_lon.")

    @model_validator(mode="after")
    def validate_shape(self) -> GeoQueryBase:
        radius_fields = (self.lat, self.lon, self.radius_m)
        box_fields = (self.min_lat, self.max_lat, self.min_lon, self.max_lon)

        has_any_radius = self._has_any(radius_fields)
        has_all_radius = self._has_all(radius_fields)
        has_any_box = self._has_any(box_fields)
        has_all_box = self._has_all(box_fields)

        if not has_any_radius and not has_any_box:
            raise ValueError(
                "Specify either lat/lon/radius_m or bounding box bounds."
            )
        if has_any_radius and not has_all_radius:
            raise ValueError(
                "lat, lon, and radius_m must be provided together."
            )
        if has_any_box and not has_all_box:
            raise ValueError(
                "min_lat, max_lat, min_lon, "
                "and max_lon must be provided together."
            )
        if has_all_radius and has_all_box:
            raise ValueError(
                "Specify either radius search or bounding box, not both."
            )
        if has_all_box:
            self._validate_bounds()
        return self
