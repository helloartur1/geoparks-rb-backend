from sqlalchemy import text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from .orm_database import sync_engine, sync_session_factory, Base
from .orm_models import route_points, routes
from models.models import routeDTO
import asyncio


class SyncConn():


    @staticmethod
    def create_table():
        Base.metadata.drop_all(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = False


    @staticmethod
    def insert_data_into_routes_and_points():
        with sync_session_factory() as session:
            routes_v = [
                {
                    "id": "3313d02d-ffad-4201-8420-d42d1c1b7bc9",
                    "name": "test",
                    "description": "test",
                    "user_id": 1
                },
                {
                    "id": "3313d02d-ffad-4201-8420-d42d1c1b7bc8",
                    "name": "test2",
                    "description": "test2",
                    "user_id": 1
                }
            ]
            points = [
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263647",
                    "order": 1,
                    "name": "test",
                    "longitude": 33.23,
                    "latitude": 55.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc320",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc9"
                },
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263648",
                    "order": 2,
                    "name": "test2",
                    "longitude": 43.23,
                    "latitude": 45.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc321",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc9"
                },
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263645",
                    "order": 1,
                    "name": "test",
                    "longitude": 23.23,
                    "latitude": 25.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc322",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc8"
                },
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263646",
                    "order": 2,
                    "name": "test2",
                    "longitude": 63.23,
                    "latitude": 65.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc323",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc8"
                }
            ]
            insert_routes = insert(routes).values(routes_v)
            insert_points = insert(route_points).values(points)
            session.execute(insert_routes)
            session.execute(insert_points)
            session.commit()
        

    @staticmethod
    def select_routes_with_selectin_relationship(user_id_from_service):
        with sync_session_factory() as session:
            query = (
                select(routes)
                .options(selectinload(routes.route_points))
                .where(routes.user_id == user_id_from_service)
            )

            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [routeDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto


# SyncConn.create_table()
# SyncConn.insert_data_into_routes_and_points()
# SyncConn.select_routes_with_selectin_relationship()


# @staticmethod
# async def insert_data():
#     async with async_session_factory() as session:
#         test_object = test(name="new name")
#         second_test_object = test(name="second new test name")
#         session.add_all([test_object, second_test_object])
#         await session.commit()


# asyncio.run(insert_data())