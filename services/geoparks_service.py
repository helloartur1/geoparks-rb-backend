from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy import UUID
from database.methods.geoparks_methods import SyncConn
from pydantic import UUID4
from models import models
from auth.auth_func.validate_func import get_current_active_auth_user


router = APIRouter(
    prefix="/geoparks",
    tags=["geoparks"]
)


@router.get("/")
async def get_geoparks():
    return SyncConn.select_all_geoparks()


@router.get("/{geopark_id}")
async def get_geopark_by_id(geopark_id: UUID4):
    return SyncConn.select_geopark_by_id(geopark_id)


@router.get("/by_geopark/{geopark_id}")  # geppark_id теперь в пути
async def get_users_points_by_geopark_id(geopark_id: UUID4):
    points = SyncConn.select_users_points_by_geopark_id(geopark_id)
    return points

@router.post("/{geopark_id}")
async def create_user_point(
    geopark_id: UUID4,
    point_data: models.UsersPoint,
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    try:
        # Генерация ID для новой точки
        point_id = uuid4()
        
        # Вставка в БД
        SyncConn.insert_user_point(
            id=point_id,
            type=point_data.Type,
            pathphoto=point_data.pathphoto,  # Просто передаём строку
            comment=point_data.Comment,
            latitude=point_data.latitude,
            longitude=point_data.longitude,
            geopark_id=geopark_id,
            user_id=current_user.id
        )
        
        return {"status": "success", "point_id": str(point_id)}
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка создания точки: {str(e)}"
        )
    
@router.delete("/point/{point_id}")
async def delete_user_point(
    point_id: UUID4,
):
    try:
        deleted = SyncConn.delete_user_point(point_id=point_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Точка не найдена или доступ запрещён.")
        return {"status": "success", "message": "Точка успешно удалена."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка удаления точки: {str(e)}")