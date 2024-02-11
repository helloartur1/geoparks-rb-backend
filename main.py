from fastapi import FastAPI
from services import admin_service, auth_service, geoobjects_service, geoparks_service, photo_service


app = FastAPI()


app.include_router(admin_service.router)
app.include_router(auth_service.router)
app.include_router(geoobjects_service.router)
app.include_router(geoparks_service.router)
app.include_router(photo_service.router)