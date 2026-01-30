from typing import Annotated

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    parent_id: Annotated[int | None, Field(default=None, ge=1)]


class ActivityOut(BaseModel):
    id: int
    name: str
    parent_id: Annotated[int | None, Field(default=None, ge=1)]
