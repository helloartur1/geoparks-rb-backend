from sqlalchemy import text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from database.config.orm_database import sync_engine, sync_session_factory, Base
from database.config.orm_models import photo
from models.models import PhotoModel
import asyncio


class SyncConn():


    @staticmethod
    def select_photo_by_name(name):
        with sync_session_factory() as session:
            query = (
                select(photo)
                .where(photo.name == name)
            )
            res = session.execute(query).first()
            result_orm = res[0]
            result_dto = PhotoModel.model_validate(result_orm, from_attributes=True)

            if result_dto:
                return result_dto
            else:
                return False
    
    
    @staticmethod
    def select_photo_by_geoobject_id(geoobject_id):
        with sync_session_factory() as session:
            query = (
                select(photo)
                .where(photo.geoobject_id == geoobject_id)
            )
            res = session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [PhotoModel.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto
        

    @staticmethod
    def insert_photo(id, path, geoobject_id, preview, name):
        with sync_session_factory() as session:
            stmt = (
                insert(photo)
                .values(
                    id=id,
                    path=path,
                    geoobject_id=geoobject_id,
                    preview=preview,
                    name=name
                )
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_photo_path(path_to_old_photo, path_to_new_photo, new_name):
        with sync_session_factory() as session:
            stmt = (
                update(photo)
                .where(photo.path == path_to_old_photo)
                .values(
                    path=path_to_new_photo,
                    name=new_name
                )
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def delete_photo(name):
        with sync_session_factory() as session:
            stmt = (
                delete(photo)
                .where(photo.name == name)
            )
            session.execute(stmt)
            session.commit()