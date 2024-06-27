from fastapi import FastAPI
from auth.auth_services import admin_service, auth_service
from services import (
    geoobjects_service, 
    geoparks_service, 
    photo_service, 
    routes_service
)
from auth.auth_services import (
    user_service
)
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import environ


env = environ.Env()
environ.Env.read_env('.env')


FOLDER = env('PATH_PHOTO_GEOOBJECT', str)


app = FastAPI()
app.mount("/" + FOLDER, StaticFiles(directory=FOLDER), name=FOLDER)
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


# app.mount(path: "/Pictures" StaticFiles(directory="Pictures"), name="Pictures")
# origins = [
#     "http://localhost",
#     "http://localhost:4200",
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


app.include_router(auth_service.router)
app.include_router(admin_service.router)
app.include_router(user_service.router)
app.include_router(geoobjects_service.router)
app.include_router(geoparks_service.router)
app.include_router(photo_service.router)
app.include_router(routes_service.router)