from typing import TYPE_CHECKING, Self

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
    insert,
    literal,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.schema.base import BaseSchema

if TYPE_CHECKING:
    from api.database.schema.agency import AgencyActivity


class Activity(BaseSchema):
    __tablename__ = "activity"

    name: Mapped[ActivityName] = relationship(
        back_populates="activity",
        cascade="all, delete-orphan",
        uselist=False,
    )
    parent_link: Mapped[ActivityParent] = relationship(
        back_populates="activity",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="ActivityParent.activity_id",
    )
    child_links: Mapped[list[ActivityParent]] = relationship(
        back_populates="parent",
        foreign_keys="ActivityParent.parent_id",
    )
    agencies: Mapped[list[AgencyActivity]] = relationship(
        back_populates="activity",
    )
    ancestor_links: Mapped[list[ActivityClosure]] = relationship(
        back_populates="ancestor",
        foreign_keys="ActivityClosure.ancestor_id",
    )
    descendant_links: Mapped[list[ActivityClosure]] = relationship(
        back_populates="descendant",
        foreign_keys="ActivityClosure.descendant_id",
    )

    @classmethod
    async def create(cls, session: AsyncSession) -> Self:
        return await cls._create(session)

    @classmethod
    async def create_activity(
        cls,
        session: AsyncSession,
        name: str,
        parent_id: int | None,
    ) -> Self:
        activity = await cls.create(session)
        await ActivityName.create(
            session=session, activity_id=activity.id, name=name
        )
        await ActivityParent.create(
            session=session,
            activity_id=activity.id,
            parent_id=parent_id,
        )
        await cls._insert_activity_closure(session, activity.id, parent_id)
        return activity

    @classmethod
    async def _insert_activity_closure(
        cls,
        session: AsyncSession,
        activity_id: int,
        parent_id: int | None,
    ) -> None:
        await session.execute(
            insert(ActivityClosure).values(
                ancestor_id=activity_id,
                descendant_id=activity_id,
                depth=0,
            )
        )

        if parent_id is None:
            return

        max_depth_stmt = select(func.max(ActivityClosure.depth)).where(
            ActivityClosure.descendant_id == parent_id
        )
        max_depth = (await session.execute(max_depth_stmt)).scalar_one()
        max_depth = max_depth if max_depth is not None else 0

        if max_depth >= 3:
            raise ValueError("Activity depth limit exceeded.")

        ancestors_stmt = select(
            ActivityClosure.ancestor_id,
            literal(activity_id).label("descendant_id"),
            (ActivityClosure.depth + 1).label("depth"),
        ).where(ActivityClosure.descendant_id == parent_id)

        await session.execute(
            insert(ActivityClosure).from_select(
                ["ancestor_id", "descendant_id", "depth"],
                ancestors_stmt,
            )
        )


class ActivityName(BaseSchema):
    __tablename__ = "activity_name"
    __table_args__ = (
        UniqueConstraint("activity_id", name="uq_activity_name_activity_id"),
        Index("ix_activity_name_name", "name"),
    )

    activity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(nullable=False)

    activity: Mapped[Activity] = relationship(back_populates="name")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        activity_id: int,
        name: str,
    ) -> Self:
        return await cls._create(
            session,
            activity_id=activity_id,
            name=name,
        )

    @classmethod
    async def update_name(
        cls,
        session: AsyncSession,
        activity_id: int,
        name: str,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.activity_id == activity_id,
            name=name,
        )


class ActivityParent(BaseSchema):
    __tablename__ = "activity_parent"
    __table_args__ = (
        UniqueConstraint("activity_id", name="uq_activity_parent_activity_id"),
        CheckConstraint(
            "activity_id <> parent_id",
            name="ck_activity_parent_not_self",
        ),
    )

    activity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("activity.id", ondelete="RESTRICT"),
        nullable=True,
    )

    activity: Mapped[Activity] = relationship(
        back_populates="parent_link",
        foreign_keys=[activity_id],
    )
    parent: Mapped[Activity] = relationship(
        back_populates="child_links",
        foreign_keys=[parent_id],
    )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        activity_id: int,
        parent_id: int | None,
    ) -> Self:
        return await cls._create(
            session,
            activity_id=activity_id,
            parent_id=parent_id,
        )

    @classmethod
    async def update_parent(
        cls,
        session: AsyncSession,
        activity_id: int,
        parent_id: int | None,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.activity_id == activity_id,
            parent_id=parent_id,
        )


class ActivityClosure(BaseSchema):
    __tablename__ = "activity_closure"
    __table_args__ = (
        UniqueConstraint(
            "ancestor_id",
            "descendant_id",
            name="uq_activity_closure_ancestor_descendant",
        ),
        CheckConstraint("depth >= 0", name="ck_activity_closure_depth_min"),
        CheckConstraint("depth <= 3", name="ck_activity_closure_depth_max"),
        Index("ix_activity_closure_ancestor_depth", "ancestor_id", "depth"),
    )

    ancestor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
    )
    descendant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
    )
    depth: Mapped[int] = mapped_column(Integer, nullable=False)

    ancestor: Mapped[Activity] = relationship(
        back_populates="ancestor_links",
        foreign_keys=[ancestor_id],
    )
    descendant: Mapped[Activity] = relationship(
        back_populates="descendant_links",
        foreign_keys=[descendant_id],
    )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        ancestor_id: int,
        descendant_id: int,
        depth: int,
    ) -> Self:
        return await cls._create(
            session,
            ancestor_id=ancestor_id,
            descendant_id=descendant_id,
            depth=depth,
        )

    @classmethod
    async def update_depth(
        cls,
        session: AsyncSession,
        closure_id: int,
        depth: int,
    ) -> Self | None:
        return await cls._update(
            session,
            cls.id == closure_id,
            depth=depth,
        )
