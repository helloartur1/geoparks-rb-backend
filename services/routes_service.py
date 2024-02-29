from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException, status, UploadFile
from pydantic import UUID4
from database.orm_conn import SyncConn

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


@router.get("/")
async def get_route(current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        return SyncConn.select_routes_with_selectin_relationship()


@router.post("/")
async def post_route(routes: models.routesDTO, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        return {"data": routes}


@router.put("/")
async def put_route(current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        return


@router.delete("/")
async def delete_route(current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        return