from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    password: str
    role: str


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

# модели Артура
class GeoobjectPathModel(BaseModel):
    id : str
    name : str
    description : str
    longitude : float
    latitude : float
    type : str
    idgeopark : str
    path_photo : str


class PathModel(BaseModel):
    path : str


class GeoobjectModel(BaseModel):
    id : str
    name : str
    description : str
    longitude : float
    latitude : float
    type : str
    idgeopark : str

class Data_geoobjects(BaseModel):
    id : str
    name : str
    description : str
    longitude : float
    latitude : float
    type : str
    idgeopark : str