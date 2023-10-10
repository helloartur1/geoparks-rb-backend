from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class ChangePictures(BaseModel):
    object_id: int
    old_name: str
    new_name: str


class DeletePicture(BaseModel):
    object_id: int
    picture_name: str


class LoginResponce(BaseModel):
    token: str