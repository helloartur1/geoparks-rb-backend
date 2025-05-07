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


class user(Base):
    __tablename__ = "users"

    id: Mapped[uidpk]
    username: Mapped[str]
    password: Mapped[bytes]
    role: Mapped[str]
    is_active: Mapped[bool]


class geoobject(Base):
    __tablename__ = "geoobject"

    id: Mapped[uidpk]
    name: Mapped[str]
    type: Mapped[str]
    common_type: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    geopark_id: Mapped[UUID4] = mapped_column(ForeignKey("geoparks.id"))
    description: Mapped[str | None]

    photos: Mapped[list["photo"]] = relationship(
        back_populates="geoobject"
    )


class geopark(Base):
    __tablename__ = "geopark"

    id: Mapped[uidpk]
    name: Mapped[str]
    description: Mapped[str | None]
    latitude: Mapped[float]
    longitude: Mapped[float]
    layer_link: Mapped[str | None]


class photo(Base):
    __tablename__ = "photo"

    id: Mapped[uidpk]
    path: Mapped[str]
    geoobject_id: Mapped[UUID4] = mapped_column(ForeignKey("geoobject.id"))
    preview: Mapped[bool]
    name: Mapped[str]

    geoobject: Mapped["geoobject"] = relationship(
        back_populates="photos"
    )


class route_points(Base):
    __tablename__ = "points"

    id: Mapped[uidpk]
    route_id: Mapped[UUID4] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    order: Mapped[int]
    longitude: Mapped[float]
    latitude: Mapped[float]
    geoobject_id: Mapped[UUID4 | None]
    
    route: Mapped["routes"] = relationship(
        back_populates="route_points"
    )


class routes(Base):
    __tablename__ = "routes"

    id: Mapped[uidpk]
    name: Mapped[str]
    description: Mapped[str | None]
    user_id: Mapped[UUID4]
    # profile: Mapped[str | None]
    # start_latitude: Mapped[float | None]
    # start_longitude: Mapped[float | None]    
    route_points: Mapped[list["route_points"]] = relationship(
        back_populates="route"
    )