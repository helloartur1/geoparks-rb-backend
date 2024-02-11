from fastapi import APIRouter
from typing import List

from database import db_conn
from models import models


router = APIRouter(
    prefix="/geopark",
    tags=["geopark"]
)


@router.get("/", response_model=List[models.GeoparkModel])
async def get_geoparks():
    query = f"SELECT geopark.* FROM geopark"
    result = db_conn.query(query)

    res = [models.GeoparkModel(
            id=str(row[0]),
            name=str(row[1]),
            latitude=float(row[2]),
            longitude=float(row[3]),
            description=str(row[4])) 
            
        for row in result
    ]

    return res