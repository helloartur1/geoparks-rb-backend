from fastapi import APIRouter
from database.methods.geoparks_methods import SyncConn
from pydantic import UUID4


router = APIRouter(
    prefix="/geoparks",
    tags=["geoparks"]
)


@router.get("/")
async def get_geoparks():
    return SyncConn.select_all_geoparks()


@router.get("/{geopark_id}")
async def get_geopark_by_id(geopark_id: UUID4):
    return SyncConn.select_geopark_by_id(geopark_id)