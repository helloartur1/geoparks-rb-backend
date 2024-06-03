from fastapi import APIRouter
from database.methods.geoparks_methods import SyncConn


router = APIRouter(
    prefix="/geoparks",
    tags=["geoparks"]
)


@router.get("/")
async def get_geoparks():
    return SyncConn.select_all_geoparks()