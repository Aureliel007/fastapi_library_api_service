import datetime
from typing import Literal

from pydantic import BaseModel


class ItemId(BaseModel):
    id: int

class StatusResponse(BaseModel):
    status: Literal["ok", "deleted"]

class Author(BaseModel):
    name: str
    biography: str
    date_of_birth: datetime.date

class UpdateAuthor(BaseModel):
    name: str | None = None
    biography: str | None = None
    date_of_birth: datetime.date | None = None