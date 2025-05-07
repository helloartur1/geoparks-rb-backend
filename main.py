from fastapi import FastAPI, Request
import httpx
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
    "http://172.20.10.2:4200",
    "http://178.214.249.0",
    "http://localhost:8080",
    "http://192.168.1.7:8080",
    "http://127.0.0.1:8080",
    "http://192.168.1.112:8080",
    "http://192.168.1.112"
    "http://172.20.10.2:8080"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_service.router)
app.include_router(admin_service.router)
app.include_router(user_service.router)
app.include_router(geoobjects_service.router)
app.include_router(geoparks_service.router)
app.include_router(photo_service.router)
app.include_router(routes_service.router)


ORS_API_KEY = "5b3ce3597851110001cf6248f0d961a50bc04e17b315f4ccec8fe8de"
ORS_ENDPOINT = "https://api.openrouteservice.org/v2/directions"

@app.post("/proxy/openrouteservice")
async def proxy_ors(request: Request):
    body = await request.json()
    print(body)
    coordinates = body.get("coordinates")
    profile = body.get("profile", "foot-walking")
    radiuses = body.get("radiuses", [])
    instructions = body.get("instructions", False)

    url = f"{ORS_ENDPOINT}/{profile}/geojson"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "coordinates": coordinates,
        "radiuses": radiuses,
        "instructions": instructions
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        print(response.status_code, " ",response)
        return response.json()