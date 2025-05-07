from fastapi import (
    Depends, 
    HTTPException, 
    status
)
from fastapi import APIRouter
from typing import Annotated
from pydantic import UUID4
from database.methods.routes_methods import SyncConn
from fastapi.encoders import jsonable_encoder
from models import models
from auth.auth_func.validate_func import get_current_active_auth_user
import environ
import uuid


env = environ.Env()
environ.Env.read_env('.env')


router = APIRouter(
    prefix="/route",
    tags=["route"]
)


@router.get("/all/")
async def get_routes():
    return SyncConn.select_routes_with_selectin_relationship()


@router.get("/{route_id}")
async def get_route_by_id(
    route_id: UUID4, 
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user:
        return SyncConn.select_route_from_route_id_and_user_id(route_id, current_user.id)
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )


@router.get("/user/{user_id}")
async def get_route(user_id: UUID4):
    return SyncConn.select_routes_with_selectin_relationship_for_user(user_id)


@router.post("/")
async def post_route(
    routesAndPoints: models.routeAndPoints, 
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user:
        if routesAndPoints.route and routesAndPoints.points:
            route_id = uuid.uuid4()
            route = routesAndPoints.route
            points = routesAndPoints.points

            SyncConn.insert_route_into_routes(route_id, route, current_user.id)
            points_arr = []
            
            for point in points:
                point_id = uuid.uuid4()
                point_post = dict(
                    id=point_id,
                    route_id=route_id,
                    order=point.order,
                    longitude=point.longitude,
                    latitude=point.latitude,
                    geoobject_id=point.geoobject_id
                )
                points_arr.append(point_post)
            
            SyncConn.insert_points_into_points(points_arr)

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully created"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is empty"
        )
    
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/system_routes/{geopark_id}")
async def get_route_by_geopark(geopark_id: UUID4):
    return SyncConn.select_route_by_geopark_id(geopark_id)


@router.put("/")
async def put_route(
    route_id: UUID4,
    route_change: models.routeAndPointsChangeModel, 
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user:
        if route_change:
            if route_change.route:
                json_compatible_route_data = route_change.route

                if json_compatible_route_data.name:
                    SyncConn.update_route_name(json_compatible_route_data, current_user.id, route_id)
                
                if json_compatible_route_data.description:
                    SyncConn.update_route_description(json_compatible_route_data, current_user.id, route_id)

                if json_compatible_route_data.profile:
                    SyncConn.update_route_profile(json_compatible_route_data, current_user.id, route_id)

                if json_compatible_route_data.start_latitude:
                    SyncConn.update_route_start_latitude(json_compatible_route_data, current_user.id, route_id)

                if json_compatible_route_data.start_longitude:
                    SyncConn.update_route_start_longitude(json_compatible_route_data, current_user.id, route_id)

            if route_change.points: #к обсуждению
                points = route_change.points

                SyncConn.delete_points_by_route_id(route_id)
                points_arr = []
            
                for point in points:
                    point_id = uuid.uuid4()
                    point_post = dict(
                        id=point_id,
                        route_id=route_id,
                        order=point.order,
                        longitude=point.longitude,
                        latitude=point.latitude,
                        geoobject_id=point.geoobject_id
                    )
                    points_arr.append(point_post)

                SyncConn.insert_points_into_points(points_arr)

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully updated"
            )
                
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is empty"
        )
    
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/")
async def delete_route(
    route_id: UUID4,
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user:
        if SyncConn.select_route_from_route_id_and_user_id(route_id, current_user.id):
            SyncConn.delete_route(route_id)

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully deleted"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Route not found"
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )