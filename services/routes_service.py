from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, Body, HTTPException, status, UploadFile
from pydantic import UUID4
from database.orm_conn import SyncConn

from fastapi.encoders import jsonable_encoder

from database import db_conn
from models import models
from jwt.token_func import get_active_user

import environ


env = environ.Env()
environ.Env.read_env('.env')


router = APIRouter(
    prefix="/route",
    tags=["route"]
)


@router.get("/all")
async def get_routes(current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user:
        return SyncConn.select_routes_with_selectin_relationship()


@router.get("/{user_id}")
async def get_route(user_id: int, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        return SyncConn.select_routes_with_selectin_relationship_for_user(user_id)


@router.post("/create")
async def post_route(routesAndPoints: models.routesAndPointsPost, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        if routesAndPoints:
            if routesAndPoints.route:
                SyncConn.insert_route_into_routes(routesAndPoints.route)
                return {"маршрут создан"}
            
            if routesAndPoints.points:
                json_compatible_points_data = jsonable_encoder(routesAndPoints.points)
                SyncConn.insert_points_into_points(json_compatible_points_data)
                return {"точки маршрута созданы"}
            
        else:
            return {"пусто"}


@router.put("/")
async def put_route(route_change: models.routeAndPointsChangeModel, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        if route_change:
            if route_change.route:
                json_compatible_route_data = route_change.route

                if json_compatible_route_data.name:
                    SyncConn.update_route_name(json_compatible_route_data)
                
                if json_compatible_route_data.description:
                    SyncConn.update_route_description(json_compatible_route_data)

                if json_compatible_route_data.user_id:
                    SyncConn.update_route_user_id(json_compatible_route_data)

                return {"сведения маршрута изменены"}
            
            if route_change.points:
                json_compatible_change_data = jsonable_encoder(route_change.points)
                SyncConn.update_points_order(json_compatible_change_data)
                return {"порядок точек изменен"}
            
    return {"плохие данные"}


@router.delete("/")
async def delete_route(route_id: UUID4, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        if route_id:
            SyncConn.delete_route(route_id)
            SyncConn.delete_route_points(route_id)

            return {"данные удалены"}
        
        return {"плохие данные"}