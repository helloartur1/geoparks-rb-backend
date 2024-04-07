from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException, status, UploadFile
from pydantic import UUID4

from database import db_conn
from models import models
from jwt.token_func import get_active_user

import environ


env = environ.Env()
environ.Env.read_env('.env')


PATH_PHOTO_GEOOBJECT = env('PATH_PHOTO_GEOOBJECT', str)


router = APIRouter(
    prefix="/photo",
    tags=["photo"]
)


@router.get("/geoobject/{geoobject_id}")
async def photos_by_geoobject(geoobject_id: UUID4):
    query = f"SELECT photo.* FROM photo WHERE geoobject_id = '{geoobject_id}'"
    result = db_conn.query(query)

    res = [models.PhotoModel(
            path=str(row[0]),
            id=str(row[2]),
            geoobjectId=str(row[1]),
            preview=bool(row[3])) 
        
        for row in result
    ]

    return res


@router.post("/")
async def add_photo_by_id_geoobject(geoobject_id: UUID4, path_photo: str, preview_photo: bool, file: UploadFile):
    # id = str(uuid.uuid4())
    # path_photo = "/geopark_image/" + path_photo
    # query = f"INSERT INTO photo(id,path,preview,geoobject_id) VALUES('{id}','{path_photo}','{preview_photo}','{geoobject_id}');"

    # return db_conn.query(query)
    return file


@router.put("/")  # роут для изменения фотки в БД
async def change_photo(pictures_name: models.ChangePictures,
                       current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        old_name = pictures_name.old_name
        new_name = pictures_name.new_name
        query_for_change = f"UPDATE photo SET path = '{PATH_PHOTO_GEOOBJECT}\{new_name}.jpg' WHERE path like '%\{old_name}.jpg%'"

        return db_conn.query(query_for_change)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@router.delete("/")  # роут для удаления фотки
async def delete_photo(picture_name: models.DeletePicture,
                       current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        delete_picture = picture_name.picture_name
        query_for_delete = f"DELETE FROM photo WHERE path = '{PATH_PHOTO_GEOOBJECT}\{delete_picture}.jpg'"

        return db_conn.query(query_for_delete)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )