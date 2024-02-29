import asyncio
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, text, String
from .orm_config import settings


sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10,
)


# async_engine = create_async_engine(
#     url=settings.DATABASE_URL_asyncpg,
#     echo=False,
#     # pool_size=5,
#     # max_overflow=10,
# )


sync_session_factory = sessionmaker(sync_engine)
# async_session_factory = async_sessionmaker(async_engine)


# str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    # type_annotation_map = {
    #     str_256: String(256)
    # }

    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"