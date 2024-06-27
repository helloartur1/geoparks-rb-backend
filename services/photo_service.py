from fastapi import (
    Depends, 
    HTTPException, 
    status, 
    UploadFile
)
from fastapi import APIRouter
from typing import Annotated
from pydantic import UUID4
from database.methods.photo_methods import SyncConn
from models import models
from auth.auth_func.validate_func import get_current_active_auth_user
import environ
import uuid
import os


env = environ.Env()
environ.Env.read_env('.env')


PATH_PHOTO_GEOOBJECT = env('PATH_PHOTO_GEOOBJECT', str)
PHOTO_FOLDER = env('PHOTO_FOLDER', str)


router = APIRouter(
    prefix="/photo",
    tags=["photo"]
)


@router.get("/{geoobject_id}")
async def photos_by_geoobject(geoobject_id: UUID4):
    return SyncConn.select_photo_by_geoobject_id(geoobject_id)


@router.post("/")
async def add_photo(
    geoobject_id: UUID4, 
    preview: bool, 
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)],
    file: list[UploadFile]
):
    if current_user.role == "admin":
        if file:
            for photo in file:
                if photo.content_type == "image/jpeg" or photo.content_type == "image/png":
                    id = uuid.uuid4()
                    path = PATH_PHOTO_GEOOBJECT + '\\' + photo.filename
                    # valid_path_to_photo = PHOTO_FOLDER + '/' + photo.filename

                    SyncConn.insert_photo(id, path, geoobject_id, preview, photo.filename)

                    contents = await photo.read()
                    with open(f"{path}", "wb") as f:
                        f.write(contents)

                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Bad type of photograph"
                    )
            
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully added"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad type of photograph"
        )
        
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.put("/") 
async def change_photo(
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)],
    old_photo: str, # image.jpg | image.img
    file: UploadFile
):
    if current_user.role == "admin":
        new_photo = file.filename
        path_to_old_photo = PATH_PHOTO_GEOOBJECT + '\\\\' + old_photo
        path_to_new_photo = PATH_PHOTO_GEOOBJECT + '\\\\' + new_photo
        valid_path_to_old_photo = PHOTO_FOLDER + '/' + old_photo
        valid_path_to_new_photo = PHOTO_FOLDER + '/' + new_photo

        if SyncConn.select_photo_by_name(old_photo):
            os.remove(path_to_old_photo)

            contents = await file.read()
            with open(f"{path_to_new_photo}", "wb") as f:
                f.write(contents)

            SyncConn.update_photo_path(valid_path_to_old_photo, valid_path_to_new_photo, new_photo)

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully updated"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad name old photograph"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/")
async def delete_photo(
    photo_name: str,
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user.role == "admin":
        path_to_photo = PATH_PHOTO_GEOOBJECT + '\\\\' + photo_name

        if SyncConn.select_photo_by_name(photo_name):
            if os.path.exists(path_to_photo):
                os.remove(path_to_photo)
                SyncConn.delete_photo(photo_name)

                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="Successfully deleted"
                )
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File not exist"
                )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad name old photograph"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )