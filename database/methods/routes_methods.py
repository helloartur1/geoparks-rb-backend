import uuid
from sqlalchemy import func, text, insert, select, update, delete 
from sqlalchemy.orm import selectinload
from database.config.orm_database import sync_engine, sync_session_factory, Base
from database.config.orm_models import RouteScore, geoobject, geopark, route_points, routes, user
from models.models import routeDTO, routePointDTO, RouteDTO1

import asyncio


class SyncConn():


    # @staticmethod
    # def create_table():
    #     Base.metadata.drop_all(sync_engine)
    #     sync_engine.echo = False
    #     Base.metadata.create_all(sync_engine)
    #     sync_engine.echo = False


    @staticmethod
    def insert_route_into_routes(route_id, route, user_id):
        with sync_session_factory() as session:
            insert_route = insert(routes).values(id=route_id,
                                                 name=route.name,
                                                 description=route.description,
                                                 user_id=user_id,
                                                #  profile=route.profile,
                                                #  start_latitude=route.start_latitude,
                                                )
            session.execute(insert_route)
            session.commit()


    @staticmethod
    def insert_points_into_points(points):
        with sync_session_factory() as session:
            stmt = (
                insert(route_points)
                .values(points)
            )
            session.execute(stmt)
            session.commit()


    '''@staticmethod
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
                    "longitude": 33.23,
                    "latitude": 55.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc320",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc9"
                },
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263648",
                    "order": 2,
                    "longitude": 43.23,
                    "latitude": 45.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc321",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc9"
                },
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263645",
                    "order": 1,
                    "longitude": 23.23,
                    "latitude": 25.55,
                    "geoobject_id": "44a04716-906a-4970-bea2-7a43414dc322",
                    "route_id": "3313d02d-ffad-4201-8420-d42d1c1b7bc8"
                },
                {
                    "id": "96f23f47-cc34-45ce-bde8-334367263646",
                    "order": 2,
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
            session.commit()'''
        

    @staticmethod
    def select_routes_with_selectin_relationship_for_user(user_id_from_service):
        with sync_session_factory() as session:
            query = (
                select(routes)
                .options(selectinload(routes.route_points))
                .where(routes.user_id == user_id_from_service)
            )

            res = session.execute(query)
            result_orm = res.scalars().all()
            print(result_orm)
            result_dto = [routeDTO.model_validate(row, from_attributes=True) for row in result_orm]
            return result_dto
        

    @staticmethod
    def select_routes_with_selectin_relationship():
        with sync_session_factory() as session:
            query = (
                select(routes)
                .options(selectinload(routes.route_points))
            )

            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [routeDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto
        

    @staticmethod
    def update_route_name(route, user_id, route_id):
        with sync_session_factory() as session:
            stmt = (
                update(routes)
                .where(
                    routes.user_id == user_id,
                    routes.id == route_id)
                .values(name=route.name)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_route_description(route, user_id, route_id):
        with sync_session_factory() as session:
            stmt = (
                update(routes)
                .where(
                    routes.user_id == user_id,
                    routes.id == route_id)
                .values(description=route.description)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_route_profile(route, user_id, route_id):
        with sync_session_factory() as session:
            stmt = (
                update(routes)
                .where(
                    routes.user_id == user_id,
                    routes.id == route_id)
                .values(profile=route.profile)
            )
            session.execute(stmt)
            session.commit()

        
    @staticmethod
    def update_route_start_latitude(route, user_id, route_id):
        with sync_session_factory() as session:
            stmt = (
                update(routes)
                .where(
                    routes.user_id == user_id,
                    routes.id == route_id)
                .values(start_latitude=route.start_latitude)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def update_route_start_longitude(route, user_id, route_id):
        with sync_session_factory() as session:
            stmt = (
                update(routes)
                .where(
                    routes.user_id == user_id,
                    routes.id == route_id)
                .values(start_longitude=route.start_longitude)
            )
            session.execute(stmt)
            session.commit()
            

    @staticmethod
    def delete_points_by_route_id(route_id):
        with sync_session_factory() as session:
            stmt = (
                delete(route_points)
                .where(route_points.route_id == route_id)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def delete_route(id):
        with sync_session_factory() as session:
            stmt = (
                delete(routes)
                .where(routes.id == id)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def delete_route_points(id):
        with sync_session_factory() as session:
            stmt = (
                delete(route_points)
                .where(route_points.route_id == id)
            )
            session.execute(stmt)
            session.commit()


    @staticmethod
    def select_route_id_from_user_id(user_id):
        with sync_session_factory() as session:
            query = (
                select(routes.id)
                .where(routes.user_id == user_id)
            )
            res = session.execute(query).first()

            if res:
                route_id = res[0]
                return route_id
            else:
                return None
            

    @staticmethod
    def select_route_from_route_id_and_user_id(route_id, user_id):
        with sync_session_factory() as session:
            query = (
                select(routes)
                .where(routes.id == route_id)
                .where(routes.user_id == user_id)
                .options(selectinload(routes.route_points))
            )
            res = session.execute(query)
            if res:
                result_orm = res.scalars().all()
                result_dto = [routeDTO.model_validate(row, from_attributes=True) for row in result_orm]
                return result_dto
            else:
                return False
            
    @staticmethod
    def select_route_by_geopark_id(geopark_id):  
        with sync_session_factory() as session:
            print(f"Executing query with geopark id: {geopark_id}")
            
            query = (  
                select(routes).distinct()   # Set 'routes' as the root entity in the select statement
                .join(route_points, routes.id == route_points.route_id)  
                .join(geoobject, route_points.geoobject_id == geoobject.id)  
                .join(geopark, geoobject.geopark_id == geopark.id)  
                .where(geopark.id == geopark_id)  
                .options(selectinload(routes.route_points))  
            )
            
            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            
            # Convert the result to DTO format
            result_dto = [routeDTO.model_validate(row, from_attributes=True) for row in result_orm]
            return result_dto


            

    @staticmethod
    def select_route_by_geopark_id(geopark_id):  
        with sync_session_factory() as session:
            print(f"Executing query with geopark id: {geopark_id}")
            
            query = (  
                select(routes).distinct()  # Set 'routes' as the root entity in the select statement
                .join(route_points, routes.id == route_points.route_id)  
                .join(geoobject, route_points.geoobject_id == geoobject.id)  
                .join(geopark, geoobject.geopark_id == geopark.id)  
                .where(geopark.id == geopark_id)  
                .options(selectinload(routes.route_points))  
            )
            
            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            
            # Convert the result to DTO format
            result_dto = [routeDTO.model_validate(row, from_attributes=True) for row in result_orm]
            return result_dto

    @staticmethod
    def insert_route_score(route_id, user_id, score):
        """Добавляет новую оценку маршрута"""
        with sync_session_factory() as session:
            score_id = uuid.uuid4()
            stmt = (
                insert(RouteScore)
                .values(
                    id=score_id,
                    route_id=route_id,
                    user_id=user_id,
                    score=score
                )
            )
            session.execute(stmt)
            session.commit()
            return score_id

    @staticmethod
    def get_route_score_stats(route_id):
        """Возвращает статистику оценок маршрута"""
        with sync_session_factory() as session:
            # Запрос для средней оценки
            avg_query = (
                select(func.avg(RouteScore.score))
                .where(RouteScore.route_id == route_id)
            )
            average_score = session.execute(avg_query).scalar()
            
            # Запрос для количества оценок
            count_query = (
                select(func.count(RouteScore.score))
                .where(RouteScore.route_id == route_id)
            )
            score_count = session.execute(count_query).scalar()
            
            return {
                "average_score": float(average_score) if average_score is not None else 0,
                "total_ratings": score_count if score_count else 0
            }
        
        
    @staticmethod
    def get_user_score_for_route(route_id, user_id):
        """Проверяет, есть ли уже оценка от пользователя для маршрута"""
        with sync_session_factory() as session:
            query = (
                select(RouteScore)
                .where(
                    RouteScore.route_id == route_id,
                    RouteScore.user_id == user_id
                )
            )
            return session.execute(query).scalar_one_or_none()