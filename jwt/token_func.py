from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Annotated
from jose import jwt, JWTError
import environ


from database import db_conn
from models import models


env = environ.Env()
environ.Env.read_env('.env')


SECRET_KEY = env('SECRET_KEY')
ALGORITHM = env('ALGORITHM')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=env('TOKEN_URL'))


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):  # создание токена
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_user(username: str):  # получение информации о пользователе из БД
    qry_username = f"SELECT * FROM users WHERE username = '{username}'"
    qry_username_result = db_conn.query(qry_username)

    user = models.User(
        id=int(qry_username_result[0][0]),
        username=qry_username_result[0][1],
        password=qry_username_result[0][2],
        role=qry_username_result[0][3],
    )

    dict_for_user = {
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }

    return dict_for_user


def get_user_from_token(
        token: Annotated[str, Depends(oauth2_scheme)]):  # получение пользователя из полезной нагрузки токена
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = models.TokenData(username=username)


    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


def get_active_user(user_from_token: Annotated[models.User, Depends(
    get_user_from_token)]):  # получение пользователя (декоратор для user from token)
    return user_from_token


def get_user_from_db(username: str,
                     password: str):  # получение айдишника пользователя из бд для проверки наличия пользователя
    id_query = f"SELECT id FROM users WHERE username = '{username}' and password = '{password}'"
    id_from_db = db_conn.query(id_query)[0][0]

    if id_from_db:
        return True

    return False