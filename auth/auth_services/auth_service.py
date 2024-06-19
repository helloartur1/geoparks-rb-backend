from fastapi import APIRouter, Depends
from auth.auth_func.validate_func import validate_auth_user
from auth.auth_func import token_func
from models.models import UserDTO, TokenInfo
from fastapi.encoders import jsonable_encoder


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
 

@router.post("/sign_in/", response_model=TokenInfo)
async def auth(user: UserDTO = Depends(validate_auth_user)):
    json_compatible_change_user = jsonable_encoder(user.id)
    jwt_payload = {
        "id": json_compatible_change_user,
        "sub": user.username,
        "role": user.role,
        "is_active": user.is_active
    }

    token = token_func.encode_jwt(jwt_payload)

    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )
    # return token_func.test()