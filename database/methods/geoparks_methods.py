from sqlalchemy import text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from database.config.orm_database import sync_engine, sync_session_factory, Base
from database.config.orm_models import geopark
from models.models import GeoparkModel
import asyncio


class SyncConn():
    
    
    @staticmethod
    def select_all_geoparks():
        with sync_session_factory() as session:
            query = (select(geopark))
            res = session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [GeoparkModel.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto


    @staticmethod
    def select_geopark_by_id(geopark_id):
        with sync_session_factory() as session:
            query = (
                select(geopark)
                .where(geopark.id == geopark_id)
            )
            res = session.execute(query)
            result_orm = res.scalars().first()
            result_dto = GeoparkModel.model_validate(result_orm, from_attributes=True)

            return result_dto