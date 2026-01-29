from typing import TYPE_CHECKING, Self

from geoalchemy2 import Geometry, WKBElement, WKTElement
from sqlalchemy import BigInteger, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.schema.base import BaseSchema

if TYPE_CHECKING:
    from api.database.schema.agency import AgencyBuilding


class Building(BaseSchema):
    __tablename__ = "building"

    address: Mapped[BuildingAddress] = relationship(
        back_populates="building",
        cascade="all, delete-orphan",
        uselist=False,
    )
    geo: Mapped[BuildingGeo] = relationship(
        back_populates="building",
        cascade="all, delete-orphan",
        uselist=False,
    )
    agencies: Mapped[list[AgencyBuilding]] = relationship(
        back_populates="building",
    )

    @classmethod
    async def create(cls, session: AsyncSession) -> Self:
        return await cls._create(session)


class BuildingAddress(BaseSchema):
    __tablename__ = "building_address"
    __table_args__ = (
        UniqueConstraint(
            "building_id", name="uq_building_address_building_id"
        ),
        Index("ix_building_address_address", "address"),
    )

    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("building.id", ondelete="CASCADE"),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(nullable=False)

    building: Mapped[Building] = relationship(back_populates="address")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        building_id: int,
        address: str,
    ) -> Self:
        return await cls._create(
            session,
            building_id=building_id,
            address=address,
        )

    @classmethod
    async def update_address(
        cls,
        session: AsyncSession,
        building_id: int,
        address: str,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.building_id == building_id,
            address=address,
        )


class BuildingGeo(BaseSchema):
    __tablename__ = "building_geo"
    __table_args__ = (
        UniqueConstraint("building_id", name="uq_building_geo_building_id"),
        Index(
            "ix_building_geo_geom",
            "geom",
            postgresql_using="gist",
        ),
    )

    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("building.id", ondelete="CASCADE"),
        nullable=False,
    )
    geom: Mapped[WKBElement] = mapped_column(
        Geometry(
            geometry_type="POINT",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    )

    building: Mapped[Building] = relationship(back_populates="geo")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        building_id: int,
        lat: float,
        lon: float,
    ) -> Self:
        point = WKTElement(f"POINT({lon} {lat})", srid=4326)
        return await cls._create(
            session,
            building_id=building_id,
            geom=point,
        )

    @classmethod
    async def update_geo(
        cls,
        session: AsyncSession,
        building_id: int,
        lat: float,
        lon: float,
    ) -> Self | None:
        point = WKTElement(f"POINT({lon} {lat})", srid=4326)
        return await cls._update(
            session,
            cls.building_id == building_id,
            geom=point,
        )
