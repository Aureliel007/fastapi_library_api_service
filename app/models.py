import datetime
from uuid import UUID

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


ORM_OBJECT = Author
ORM_CLS = type[Author]