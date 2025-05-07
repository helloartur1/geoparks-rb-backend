from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from models.models import UserDTO
from typing import Annotated
from database.methods.admin_methods import SyncConn
from auth.auth_func import token_func
from auth.auth_func import password_func
import environ


env = environ.Env()
environ.Env.read_env('.env')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=env("TOKEN_URL"))


def validate_auth_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )

    if not (user := SyncConn.select_user(form_data.username)):
        raise unauthed_exc
    
    # if not password_func.validate_password(
    #     password=form_data.password,
    #     hashed_password=user.password,
    # ):
    #     raise unauthed_exc
    
    return user


def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    try:
        payload = token_func.decode_jwt(
            token=token
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return payload


def get_current_auth_user(
    payload: Annotated[dict, Depends(get_current_token_payload)],
) -> UserDTO:
    username: str | None = payload.get("sub")
    if user := SyncConn.select_user(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid user",
    )


def get_current_active_auth_user(
    user: Annotated[UserDTO, Depends(get_current_auth_user)],
):
    if user.is_active:
        return user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user",
    )