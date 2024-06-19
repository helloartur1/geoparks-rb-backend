from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    Form
)
from auth.auth_func.validate_func import get_current_active_auth_user
from typing import Annotated
from models import models
from database.methods.admin_methods import SyncConn
from auth.auth_func import password_func
import uuid


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/users/")
async def get_all_users(current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]):
    if current_user.role== "admin":
        return SyncConn.select_all_users()
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )


@router.post("/")  # роут для создания пользователя
async def create_user(
    username: Annotated[str, Form],
    password: Annotated[str, Form],
    role: Annotated[str, Form],
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user.role == "admin":
        if not SyncConn.select_user(username):
            id = uuid.uuid4()
            password = password_func.hash_password(password)

            SyncConn.insert_user(
                id, 
                username, 
                password,
                role
            )

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully uploaded"
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with that username already exist"
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )
    

@router.put("/")  # роут для изменения роли пользователя
async def update_user_data(
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)],
    username: str,
    new_role: str | None = None,
    new_active: bool | None = None,
):
    if current_user.role == "admin":
        if new_role == None and new_active == None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request is empty"
            )
        
        if new_role != None:
            SyncConn.update_user_role(username, new_role)

        if new_active != None:
            SyncConn.update_user_active(username, new_active)

        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Successfully updated"
        )
    
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@router.delete("/")  # роут для удаления пользователя
async def delete_user(
    username: str, 
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user.role == "admin":
        SyncConn.delete_user(username)

        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Successfully deleted"
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )