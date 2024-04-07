from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from typing import Annotated, List
from pydantic import UUID4

from database import db_conn
from models import models
from jwt.token_func import get_active_user 


router = APIRouter(
    prefix="/geoobject",
    tags=["geoobject"]
)


@router.get("/", response_model=List[models.GeoobjectModel])
async def get_all_geobjects():
    query1 = f"SELECT * FROM geoobject"
    result = db_conn.query(query1)

    res = [models.GeoobjectModel(
        name=str(row[0]),
        description=str(row[1]),
        longitude=float(row[2]),
        latitude=float(row[3]),
        id=str(row[4]),
        type=str(row[5]),
        geoparkId=str(row[6]))
        for row in result
    ]
    
    return res


@router.get("/{id}", response_model=models.GeoobjectModel)
async def get_geoobject(id: UUID4):
    query = f"SELECT * FROM geoobject  WHERE id = '{id}'"
    result = db_conn.query(query)
    result = result[0]

    res =  models.GeoobjectModel(
        name=str(result[0]),
        description=str(result[1]),
        longitude=float(result[2]),
        latitude=float(result[3]),
        id=str(result[4]),
        type=str(result[5]),
        geoparkId=str(result[6])
    )
    
    return res


@router.get("/detail/{id}", response_model=models.GeoobjectModelDetail)
async def get_geoobject_and_photos(id: UUID4):
    query = (
        f"SELECT geoobject.id, geoobject.name, geoobject.description, geoobject.longitude, geoobject.latitude, geoobject.type, geoobject.idgeopark, ARRAY_AGG(photo.path) as paths from geoobject"
        f" JOIN photo ON geoobject.id = photo.geoobject_id WHERE photo.geoobject_id = '{id}' GROUP BY geoobject.id"
    )

    query_result = db_conn.query(query)
    result = query_result[0]

    res = models.GeoobjectModelDetail(
            id=str(result[0]),
            name=str(result[1]),
            description=str(result[2]),
            longitude=float(result[3]),
            latitude=float(result[4]), type=str(result[5]),
            geoparkId=str(result[6]),
            photoPaths=list(result[len(result) - 1])
    )
    
    return res


@router.get("/geopark/{geopark_id}", response_model=List[models.GeoobjectModel])
async def get_geoobjects_by_geopark(geopark_id: str):
    query = f"SELECT geoobject.* FROM geoobject  WHERE geoobject.idgeopark = '{geopark_id}';"
    result = db_conn.query(query)

    res = [models.GeoobjectModel(
            id=str(row[4]),
            name=str(row[0]),
            description=str(row[1]),
            longitude=float(row[2]),
            latitude=float(row[3]),
            type=str(row[5]),
            geoparkId=str(row[6]))

        for row in result
    ]

    return res


@router.post("/")
async def create_geoobject(new_geoobject: models.GeoobjectModel,
                           current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        if new_geoobject.name and new_geoobject.longitude and new_geoobject.latitude and new_geoobject.id and new_geoobject.type and new_geoobject.geoparkId:
            create_query = f"INSERT INTO geoobject VALUES ('{new_geoobject.name}', '{new_geoobject.description}', {new_geoobject.longitude}, {new_geoobject.latitude}, '{new_geoobject.id}', '{new_geoobject.type}', '{new_geoobject.geoparkId}')"

            return db_conn.query(create_query)
    
        else:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="some fields are empty"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@router.put("/")
async def update_geoobject(id: UUID4, new_data: models.UpdateGeoobjectModel, 
                           current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        update_query = f"UPDATE geoobject SET "

        if new_data.name:
            update_query += f"name = '{new_data.name}',"

        elif new_data.description:
            update_query += f"description = '{new_data.description}',"

        elif new_data.longitude:
            update_query += f"longitude = {new_data.longitude},"

        elif new_data.latitude:
            update_query += f"latitude = {new_data.latitude},"

        elif new_data.type:
            update_query += f"type = '{new_data.type}',"

        elif new_data.geoparkId:
            update_query += f"geoparkId = '{new_data.geoparkId}',"

        else:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields are empty"
        )

        update_query = update_query[:-1] + f" "
        update_query = update_query + f"WHERE id = '{id}'"
            
       # return update_query коммент не убирать
        return db_conn.query(update_query)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.delete("/")
async def delete_geoobject(id: UUID4, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        delete_query = f"DELETE FROM geoobject WHERE id = '{id}'"

        return db_conn.query(delete_query)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )