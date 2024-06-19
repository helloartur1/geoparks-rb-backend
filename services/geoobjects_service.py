from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from typing import Annotated, List
from pydantic import UUID4
from database.methods.geoobjects_methods import SyncConn
from models import models
from auth.auth_func.validate_func import get_current_active_auth_user
import uuid


router = APIRouter(
    prefix="/geoobject",
    tags=["geoobject"]
)


@router.get("/", response_model=List[models.GeoobjectModel])
async def get_all_geobjects():
    return SyncConn.select_all_geoobjects()


@router.get("/{id}", response_model=models.GeoobjectModel)
async def get_geoobject_by_id(id: UUID4):
    if res := SyncConn.select_geoobject_by_id(id):
        return res


@router.get("/detail/{id}")
async def get_geoobject_and_photos(id: UUID4):
    return SyncConn.select_geoobject_with_selectin_relationship_for_photo(id)


@router.get("/geopark/{geopark_id}", response_model=List[models.GeoobjectModel])
async def get_geoobjects_by_geopark(geopark_id: UUID4):
    return SyncConn.select_geoobject_by_geoprark_id(geopark_id)


@router.post("/")
async def create_geoobject(
    new_geoobject: models.InsertGeoobjectModel,
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user.role == "admin":
        geoobject_id = uuid.uuid4()
        SyncConn.insert_into_geoobject(geoobject_id, new_geoobject) #только если в связанной таблице есть геопарк, на который ссылается геообъект

        raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully created"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@router.put("/")
async def update_geoobject(id: UUID4, new_data: models.UpdateGeoobjectModel, 
                           current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]):
    if current_user.role == "admin":
        if SyncConn.select_geoobject_by_id(id):
            if new_data.name:
                SyncConn.update_geoobject_name(id, new_data.name)

            if new_data.type:
                SyncConn.update_geoobject_type(id, new_data.type)

            if new_data.commonType:
                SyncConn.update_geoobject_commonType(id, new_data.commonType)

            if new_data.longitude:
                SyncConn.update_geoobject_longitude(id, new_data.longitude)

            if new_data.latitude:
                SyncConn.update_geoobject_latitude(id, new_data.latitude)

            if new_data.geopark_id:
                SyncConn.update_geoobject_geopark_id(id, new_data.geopark_id)

            if new_data.description:
                SyncConn.update_geoobject_description(id, new_data.description)

            if not new_data:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty fields"
            )

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully updated"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad geoobject"
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )


@router.delete("/")
async def delete_geoobject(
    id: UUID4, 
    current_user: Annotated[models.UserDTO, Depends(get_current_active_auth_user)]
):
    if current_user.role == "admin":
        if SyncConn.select_geoobject_by_id(id):
            SyncConn.delete_geoobject(id)

            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Successfully deleted"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad geoobject"
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
        headers={"WWW-Authenticate": "Bearer"}
    )