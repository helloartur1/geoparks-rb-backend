from pydantic import BaseModel, UUID4
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
    commonType: str
    latitude: float
    longitude: float
    geopark_id: UUID4
    description: str | None = None


class PhotoModel(BaseModel):
    id: UUID4
    path: str
    geoobject_id: UUID4
    preview: bool
    name: str


class GeoobjectModelDTO(BaseModel):
    id: UUID4
    name: str
    type: str
    commonType: str
    latitude: float
    longitude: float
    geopark_id: UUID4
    description: str
    photos: list[PhotoModel]


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
    commonType: str
    latitude: float
    longitude: float
    geopark_id: UUID4
    description: str | None = None


class UpdateGeoobjectModel(BaseModel):
    name: str | None = None
    type: str | None = None
    commonType: str | None = None
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
    geoobject_id: UUID4


class routeDTO(BaseModel):
    id: UUID4
    name: str | None = None
    description: str | None = None
    user_id: UUID4
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
    geoobject_id: UUID4


class routePost(BaseModel):
    name: str 
    description: str | None = None


class routeAndPoints(BaseModel):
    route: routePost 
    points: list[routePointPost] 


#временно, к обсуждению
class routeChangeModel(BaseModel):
    name: str | None = None
    description: str | None = None
    
    __hash__ = object.__hash__


class pointsChangeModel(BaseModel):
    order: int
    longitude: float
    latitude: float
    geoobject_id: UUID4


class routeAndPointsChangeModel(BaseModel):
    route: routeChangeModel | None = None
    points: list[pointsChangeModel] | None = None