from sqlalchemy import text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from database.config.orm_database import sync_engine, sync_session_factory, Base
from database.config.orm_models import geoobject
from models.models import GeoobjectModel, GeoobjectModelDTO
import asyncio


class SyncConn():
    
    
    @staticmethod
    def select_all_geoobjects():
        with sync_session_factory() as session:
            query = (select(geoobject))
            res = session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [GeoobjectModel.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto
        

    @staticmethod
    def select_geoobject_by_id(geoobject_id):
        with sync_session_factory() as session:
            query = (
                select(geoobject)
                .where(geoobject.id == geoobject_id)
            )
            res = session.execute(query).first()
            result_orm = res[0]
            result_dto = GeoobjectModel.model_validate(result_orm, from_attributes=True)

            if result_dto:
                return result_dto
            else:
                return False
        

    @staticmethod
    def select_geoobject_with_selectin_relationship_for_photo(geoobject_id):
        with sync_session_factory() as session:
            query = (
                select(geoobject)
                .options(selectinload(geoobject.photos))
                .where(geoobject.id == geoobject_id)
            )
            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [GeoobjectModelDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")

            return result_dto
        

    @staticmethod
    def select_geoobject_by_geoprark_id(geopark_id):
        with sync_session_factory() as session:
            query = (
                select(geoobject)
                .where(geoobject.geopark_id == geopark_id)
            )
            res = session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [GeoobjectModel.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto
        
        

    @staticmethod
    def insert_into_geoobject(geoobject_id, new_geoobject):
        with sync_session_factory() as session:
            stmt = (
                insert(geoobject)
                .values(
                    id=geoobject_id,
                    name=new_geoobject.name,
                    type=new_geoobject.type,
                    commonType=new_geoobject.commonType,
                    latitude=new_geoobject.latitude,
                    longitude=new_geoobject.longitude,
                    geopark_id=new_geoobject.geopark_id,
                    description=new_geoobject.description
                )
            )
            session.execute(stmt)
            session.commit()

    
    @staticmethod
    def update_geoobject_name(id, name):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(name=name)
            )
            session.execute(stmt)
            session.commit()

    @staticmethod
    def update_geoobject_type(id, type):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(type=type)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_geoobject_common_type(id, common_type):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(common_type=common_type)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_geoobject_longitude(id, longitude):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(longitude=longitude)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_geoobject_latitude(id, latitude):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(latitude=latitude)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_geoobject_geopark_id(id, geopark_id):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(geopark_id=geopark_id)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_geoobject_description(id, description):
        with sync_session_factory() as session:
            stmt = (
                update(geoobject)
                .where(geoobject.id == id)
                .values(description=description)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def delete_geoobject(id):
        with sync_session_factory() as session:
            stmt = (
                delete(geoobject)
                .where(geoobject.id == id)
            )
            session.execute(stmt)
            session.commit()