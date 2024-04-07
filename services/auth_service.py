from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from jwt.token_func import get_user_from_db, get_user, create_jwt_token

import environ


env = environ.Env()
environ.Env.read_env('.env')


ACCESS_TOKEN_EXPIRE_MINUTES = env('ACCESS_TOKEN_EXPIRE_MINUTES', int)


router = APIRouter(
    prefix="/login",
    tags=["auth"]
)


@router.post("/")  # роут для аутентификации
async def auth(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_from_db = get_user_from_db(form_data.username, form_data.password)

    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = get_user(form_data.username)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token = create_jwt_token(
        data = {"id": user["id"],
                "sub": user["username"],
                "role": user["role"]}, 
        expires_delta=access_token_expires
    )

    return {"token": token}