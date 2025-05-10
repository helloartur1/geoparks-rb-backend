from sqlalchemy import text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from database.config.orm_database import sync_engine, sync_session_factory, Base
from database.config.orm_models import geopark,userpoint
from models.models import GeoparkModel, UsersPoint
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
    
    @staticmethod
    def insert_user_point(id,type,pathphoto,comment,geopark_id, user_id,latitude,longitude):
        with sync_session_factory() as session:
            query = (
                insert(userpoint)
                .values(
                    id = id,
                    Type = type,
                    pathphoto = pathphoto,
                    Comment = comment,
                    latitude = latitude,
                    longitude = longitude,
                    geoparkid=geopark_id,
                    userid=user_id
                )
            )

            session.execute(query)
            session.commit()

    @staticmethod
    def select_users_points_by_geopark_id(geopark_id):
        with sync_session_factory() as session:
            query = select(userpoint).where(userpoint.geoparkid == geopark_id)
            result = session.execute(query)
            
            points = []
            for row in result.scalars().all():
                # Преобразуем None в пустую строку
                row_dict = {**row.__dict__}
                if row_dict.get('pathphoto') is None:
                    row_dict['pathphoto'] = ""
                points.append(UsersPoint.model_validate(row_dict))
            
            return points
    @staticmethod
    def delete_user_point(point_id):
        with sync_session_factory() as session:
            query = (
                delete(userpoint)
                .where(userpoint.id == point_id)
            )
            result = session.execute(query)
            session.commit()
            return result.rowcount > 0  # True если хотя бы одна строка удалена
