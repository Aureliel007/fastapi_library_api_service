import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator, Field


class ItemId(BaseModel):
    id: int

class StatusResponse(BaseModel):
    status: Literal["ok", "deleted"]

class BaseUser(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(value) > 32:
            raise ValueError("Password must not exceed 32 characters.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter.")
        return value

class CreateUser(BaseUser):
    name: str

class GetUser(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

class GetUserDetails(GetUser):
    books: list["GetBook"]

class UpdateUser(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(value) > 32:
            raise ValueError("Password must not exceed 32 characters.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter.")
        return value

class BaseAuthor(BaseModel):
    name: str

class CreateAuthor(BaseAuthor):
    biography: str
    date_of_birth: datetime.date

class AuthorSchema(CreateAuthor):
    id: int

class UpdateAuthor(BaseModel):
    name: str | None = None
    biography: str | None = None
    date_of_birth: datetime.date | None = None

class GenreSchema(BaseModel):
    name: str

class AddBook(BaseModel):
    title: str
    description: str | None = None
    release_year: int
    authors: list[int]
    genres: list[int]
    available_stock: int

class GetBook(BaseModel):
    id: int
    title: str
    description: str
    release_year: int
    authors: list[BaseAuthor]
    genres: list[GenreSchema]
    available_stock: int

class UpdateBook(BaseModel):
    title: str | None = None
    description: str | None = None
    release_year: int | None = None
    authors: list[int] | None = None
    genres: list[int] | None = None
    available_stock: int | None = None
