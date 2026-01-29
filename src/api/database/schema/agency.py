from typing import TYPE_CHECKING, Self

from sqlalchemy import BigInteger, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.schema.base import BaseSchema

if TYPE_CHECKING:
    from api.database.schema.actiivty import Activity
    from api.database.schema.building import Building


class Agency(BaseSchema):
    __tablename__ = "agency"

    name: Mapped[AgencyName] = relationship(
        back_populates="agency",
        cascade="all, delete-orphan",
        uselist=False,
    )
    phones: Mapped[list[AgencyPhone]] = relationship(
        back_populates="agency",
        cascade="all, delete-orphan",
    )
    building_link: Mapped[AgencyBuilding] = relationship(
        back_populates="agency",
        cascade="all, delete-orphan",
        uselist=False,
    )
    activities: Mapped[list[AgencyActivity]] = relationship(
        back_populates="agency",
        cascade="all, delete-orphan",
    )

    @classmethod
    async def create(cls, session: AsyncSession) -> Self:
        return await cls._create(session)


class AgencyName(BaseSchema):
    __tablename__ = "agency_name"
    __table_args__ = (
        UniqueConstraint("agency_id", name="uq_agency_name_agency_id"),
        Index("ix_agency_name_name", "name"),
    )

    agency_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agency.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(nullable=False)

    agency: Mapped[Agency] = relationship(back_populates="name")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        agency_id: int,
        name: str,
    ) -> Self:
        return await cls._create(session, agency_id=agency_id, name=name)

    @classmethod
    async def update_name(
        cls,
        session: AsyncSession,
        agency_id: int,
        name: str,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.agency_id == agency_id,
            name=name,
        )


class AgencyPhone(BaseSchema):
    __tablename__ = "agency_phone"
    __table_args__ = (
        UniqueConstraint(
            "agency_id",
            "phone",
            name="uq_agency_phone_agency_id_phone",
        ),
        Index("ix_agency_phone_phone", "phone"),
    )

    agency_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agency.id", ondelete="CASCADE"),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(nullable=False)

    agency: Mapped[Agency] = relationship(back_populates="phones")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        agency_id: int,
        phone: str,
    ) -> Self:
        return await cls._create(session, agency_id=agency_id, phone=phone)

    @classmethod
    async def update_phone(
        cls,
        session: AsyncSession,
        phone_id: int,
        phone: str,
    ) -> Self | None:
        return await cls._update(session, cls.id == phone_id, phone=phone)


class AgencyBuilding(BaseSchema):
    __tablename__ = "agency_building"
    __table_args__ = (
        UniqueConstraint("agency_id", name="uq_agency_building_agency_id"),
        Index("ix_agency_building_building_id", "building_id"),
    )

    agency_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agency.id", ondelete="CASCADE"),
        nullable=False,
    )
    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("building.id", ondelete="RESTRICT"),
        nullable=False,
    )

    agency: Mapped[Agency] = relationship(back_populates="building_link")
    building: Mapped[Building] = relationship(back_populates="agencies")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        agency_id: int,
        building_id: int,
    ) -> Self:
        return await cls._create(
            session,
            agency_id=agency_id,
            building_id=building_id,
        )

    @classmethod
    async def update_building(
        cls,
        session: AsyncSession,
        agency_id: int,
        building_id: int,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.agency_id == agency_id,
            building_id=building_id,
        )


class AgencyActivity(BaseSchema):
    __tablename__ = "agency_activity"
    __table_args__ = (
        UniqueConstraint(
            "agency_id",
            "activity_id",
            name="uq_agency_activity_agency_id_activity_id",
        ),
        Index("ix_agency_activity_activity_id", "activity_id"),
    )

    agency_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agency.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activity.id", ondelete="RESTRICT"),
        nullable=False,
    )

    agency: Mapped[Agency] = relationship(back_populates="activities")
    activity: Mapped[Activity] = relationship(back_populates="agencies")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        agency_id: int,
        activity_id: int,
    ) -> Self:
        return await cls._create(
            session,
            agency_id=agency_id,
            activity_id=activity_id,
        )

    @classmethod
    async def update_activity(
        cls,
        session: AsyncSession,
        link_id: int,
        activity_id: int,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.id == link_id,
            activity_id=activity_id,
        )
