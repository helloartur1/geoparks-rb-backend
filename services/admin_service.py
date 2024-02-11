from fastapi import APIRouter
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from typing import Annotated


from database import db_conn
from models import models
from jwt.token_func import get_active_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/") # TEST ROUTE
async def test():
    q = f"SELECT * FROM users"
    return db_conn.query(q)


@router.get("/about_me", response_model=models.User)  # роут для проверки авторизации - выводит информацию о пользователе
async def about_me(current_user: Annotated[models.User, Depends(get_active_user)]):
    return current_user


@router.post("/")  # роут для создания пользователя
async def create_user(new_user: models.User,
                      current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_create = f"INSERT INTO users VALUES ({new_user.id}, '{new_user.username}', '{new_user.password}', '{new_user.role}')"

        return db_conn.query(qry_for_create)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@router.put("/")  # роут для изменения роли пользователя
async def update_user_role(user_username: str, new_role: str,
                           current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_update = f"UPDATE users SET role = '{new_role}' WHERE username = '{user_username}'"

        return db_conn.query(qry_for_update)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@router.delete("/")  # роут для удаления пользователя
async def delete_user(username: str, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_delete = f"DELETE FROM users WHERE username = '{username}'"

        return db_conn.query(qry_for_delete)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )