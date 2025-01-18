import datetime
from enum import Enum

from sqlalchemy import (UUID, Boolean, CheckConstraint, Column, DateTime,
                        ForeignKey, Integer, String, Table, UniqueConstraint,
                        func)
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DSN
# from extra_types import ModelName


engine = create_async_engine(DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass

book_genre = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True, index=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True, index=True),
)

book_author = Table(
    "book_author",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True, index=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True, index=True),
)

book_user = Table(
    "book_user",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True, index=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("rent_date", DateTime, nullable=False, default=datetime.datetime.now()),
    Column(
        "return_date", DateTime, nullable=True,
        default=datetime.datetime.now() + datetime.timedelta(days=7)
    ),
)

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(100), nullable=False, default=UserRole.user)
    books: Mapped[list["Book"]] = relationship("Book", secondary=book_user, lazy="joined")

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    biography: Mapped[str] = mapped_column(String(1000), nullable=False)
    date_of_birth: Mapped[datetime.date] = mapped_column(DateTime, nullable=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "biography": self.biography,
            "date_of_birth": self.date_of_birth
        }

class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    authors: Mapped[list["Author"]] = relationship(
        "Author", secondary=book_author, lazy="joined"
    )
    genres: Mapped[list["Genre"]] = relationship(
        "Genre", secondary=book_genre, lazy="joined"
    )
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "release_year": self.release_year,
            "authors": self.authors,
            "genres": self.genres,
            "available_stock": self.available_stock
        }


ORM_OBJECT = Author | Genre | Book | User
ORM_CLS = type[Author] | type[Genre] | type[Book] | type[User]
