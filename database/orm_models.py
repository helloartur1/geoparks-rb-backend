import datetime
from typing import Annotated
from sqlalchemy import MetaData, text, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .orm_database import Base
from pydantic import UUID4


intpk = Annotated[int, mapped_column(primary_key=True)]
uidpk = Annotated[UUID4, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=datetime.datetime.utcnow,
    )]


metadata_obj = MetaData()


# class test(Base):
#     __tablename__ = "test"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]


# class NewTestClass(Base):
#     __tablename__ = "second"

#     id: Mapped[intpk]
#     title: Mapped[str_256]
#     created_at: Mapped[created_at]
#     updated_at: Mapped[updated_at]


class route_points(Base):
    __tablename__ = "points"

    id: Mapped[uidpk]
    route_id: Mapped[UUID4] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    order: Mapped[int]
    name: Mapped[str | None]
    longitude: Mapped[float | None]
    latitude: Mapped[float | None]
    geoobject_id: Mapped[UUID4]
    
    route: Mapped["routes"] = relationship(
        back_populates="route_points"
    )


class routes(Base):
    __tablename__ = "routes"

    id: Mapped[uidpk]
    name: Mapped[str | None]
    description: Mapped[str | None]
    user_id: Mapped[int]
    
    route_points: Mapped[list["route_points"]] = relationship(
        back_populates="route"
    )