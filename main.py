from fastapi import FastAPI
from services import admin_service, auth_service, geoobjects_service, geoparks_service, photo_service


from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()


app = FastAPI()
app.mount("/geopark_image", StaticFiles(directory="geopark_image"), name="geopark_image")
origins = [
    "http://localhost",
    "http://localhost:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(admin_service.router)
app.include_router(auth_service.router)
app.include_router(geoobjects_service.router)
app.include_router(geoparks_service.router)
app.include_router(photo_service.router)