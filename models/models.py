from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, UUID4, Field
from sqlalchemy import UUID
from typing_extensions import List


class User(BaseModel):
    id: int
    username: str
    password: str
    role: str


class UserDTO(BaseModel):
    id: UUID4
    username: str
    password: str
    role: str
    is_active: bool

class CreateGeoobjectResponse(BaseModel):
    id: UUID4

class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ChangePictures(BaseModel):
    id: int
    old_name: str
    new_name: str


class DeletePicture(BaseModel):
    id: int
    picture_name: str


class LoginResponce(BaseModel):
    token: str


class GeoparkModel(BaseModel):
    id: UUID4
    name: str
    description: str | None = None
    latitude: float
    longitude: float
    layer_link: str | None = None


class GeoobjectModel(BaseModel):
    id: UUID4
    name: str
    type: str
    common_type: str
    latitude: float
    longitude: float
    geopark_id: UUID4
    description: str | None = None


class PhotoModel(BaseModel):
    id: UUID4 
    path: str
    geoobject_id: UUID4
    preview: bool = None
    name: str


class GeoobjectModelDTO(BaseModel):
    id: UUID4
    name: str
    type: str
    common_type: str
    latitude: float
    longitude: float
    geopark_id: UUID4
    description: str
    photos: list[PhotoModel]

class UsersPoint(BaseModel):
    id : UUID4
    Type : str 
    latitude: float
    longitude: float 
    Comment : str
    pathphoto : str = ""
    geoparkid : UUID4

# class GeoobjectModelDetail(BaseModel):
#     id: UUID4
#     name: str
#     description: str
#     longitude: float
#     latitude: float
#     type: str
#     geoparkId: str
#     photoPaths: List[str]


class PathModel(BaseModel):
    path: str


class InsertGeoobjectModel(BaseModel):
    name: str
    type: str
    common_type: str
    latitude: float
    longitude: float
    geopark_id: UUID4
    description: str | None = None


class UpdateGeoobjectModel(BaseModel):
    name: str | None = None
    type: str | None = None
    common_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    geopark_id: UUID4 | None = None
    description: str | None = None


#для selectin relationship
class routePointDTO(BaseModel):
    id: UUID4
    route_id: UUID4
    order: int
    longitude: float | None = None
    latitude: float | None = None
    geoobject_id: UUID4 | None = None


class routeDTO(BaseModel):
    id: UUID4
    name: str | None = None
    description: str | None = None
    user_id: UUID4
    route_points: list[routePointDTO]

class RouteDTO1(BaseModel):
    id: UUID4
    name: str | None = None
    description: str | None = None
    route_points: list[routePointDTO]

class routesDTO(BaseModel):
    routes: list[routeDTO]


class routePointsRelDTO(routePointDTO):
    route: "routeDTO"


class RouteRelDTO(routeDTO):
    points: list["routePointDTO"]
#для selectin relationship
    

class routePointPost(BaseModel):
    order: int
    longitude: float
    latitude: float
    geoobject_id: UUID4 | None = None


class routePost(BaseModel):
    name: str 
    description: str | None = None
    profile: str | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None


class routeAndPoints(BaseModel):
    route: routePost 
    points: list[routePointPost] 


#временно, к обсуждению
class routeChangeModel(BaseModel):
    name: str | None = None
    description: str | None = None
    profile: str | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    
    __hash__ = object.__hash__


class pointsChangeModel(BaseModel):
    order: int
    longitude: float
    latitude: float
    geoobject_id: UUID4 | None = None


class routeAndPointsChangeModel(BaseModel):
    route: routeChangeModel | None = None
    points: list[pointsChangeModel] | None = None

class RouteScoreResponse(BaseModel):
    id: UUID4
    route_id: UUID4
    user_id: UUID4
    score: int


class RouteScoreCreate(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")