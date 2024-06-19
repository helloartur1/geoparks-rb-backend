from fastapi import (
    APIRouter, 
    Depends, 
)
from auth.auth_func.validate_func import (
    get_current_token_payload,
    get_current_active_auth_user
)
from typing import Annotated
from typing import Annotated
from models import models


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/about_me/")
async def about_me(
    payload: Annotated[dict, Depends(get_current_token_payload)],
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    iat = payload.get("iat")
    return {
        "username": current_user.username,
        "role": current_user.role,
        "logged_in_at": iat,
        "is_active": current_user.is_active
    }