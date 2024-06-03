from sqlalchemy import text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from database.config.orm_database import sync_engine, sync_session_factory, Base
from database.config.orm_models import user
from models.models import UserDTO


class SyncConn():


    @staticmethod
    def select_user(username):
        with sync_session_factory() as session:
            query = (
                select(user)
                .where(user.username == username)
            )

            res = session.execute(query).first()

            if res:
                user_from_db = res[0]
                return user_from_db
            else:
                return None


    @staticmethod
    def select_all_users():
        with sync_session_factory() as session:
            query = (select(user))
            res = session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [UserDTO.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto
        

    @staticmethod
    def insert_user(id, username, password, role):
        with sync_session_factory() as session:
            stmt = (
                insert(user)
                .values(
                    id=id,
                    username=username,
                    password=password,
                    role=role,
                    is_active=True
                )
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_user_role(username, role):
        with sync_session_factory() as session:
            stmt = (
                update(user)
                .where(user.username == username)
                .values(role=role)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_user_active(username, active):
        with sync_session_factory() as session:
            stmt = (
                update(user)
                .where(user.username == username)
                .values(is_active=active)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def delete_user(username):
        with sync_session_factory() as session:
            stmt = (
                delete(user)
                .where(user.username == username)
            )
            session.execute(stmt)
            session.commit()