from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import jwt, JWTError
import models

from config import DB_HOST,DB_PASS,DB_USER,DB_PORT,DB_NAME,PATH_PHOTO_GEOOBJECT

from pydantic import UUID4
import uuid, db_conn
from fastapi import FastAPI
from models import PathModel, GeoobjectPathModel, Data_geoobjects, GeoobjectModel

conn_params = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}


app = FastAPI()


SECRET_KEY = "oPP6V7pbQsL5XYKI7HfXZQs2hp42fU96"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")


def create_jwt_token(data: dict, expires_delta: timedelta | None = None): #создание токена
    to_encode = data.copy()


    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)


    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)


    return encoded_jwt


def get_user(username: str): #получение информации о пользователе из БД
    qry_username = f"SELECT * FROM users WHERE username = '{username}'"
    qry_username_result = db_conn.query(qry_username)


    user = models.User(
        id = int(qry_username_result[0][0]),
        username = qry_username_result[0][1],
        password = qry_username_result[0][2],
        role = qry_username_result[0][3],
    )


    dict_for_user = {
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }


    return dict_for_user


def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]): #получение пользователя из полезной нагрузки токена
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )


    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get("sub")


        if username is None:
            raise credentials_exception


        token_data = models.TokenData(username = username)


    except JWTError:
        raise credentials_exception


    user = get_user(username = token_data.username)


    if user is None:
        raise credentials_exception


    return user


def get_active_user(user_from_token: Annotated[models.User, Depends(get_user_from_token)]): #???получение активного пользователя??? По сути то же что и получение пользователя из токена
    # if user_from_token.disabled:
    #     raise HTTPException(status_code = 400, detail = "Inactive user")


    return user_from_token


def get_user_from_db(username: str, password: str): #получение айдишника пользователя из бд ???для проверки наличия пользователя???
    id_query = f"SELECT id FROM users WHERE username = '{username}' and password = '{password}'"
    id_from_db = db_conn.query(id_query)[0][0]


    if id_from_db:
        return True


    return False


@app.get("/test")
async def test():
    q = f"SELECT * FROM users"
    return db_conn.query(q)


@app.post("/login") #роут для аутентификации
async def auth(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_from_db = get_user_from_db(form_data.username, form_data.password)


    if not user_from_db:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )


    user = get_user(form_data.username)
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)


    token = create_jwt_token(
        data = {"sub": user["username"]}, expires_delta = access_token_expires
    )


    return {"token": token}


@app.get("/about_me", response_model = models.User) #роут для проверки авторизации - выводит информацию о пользователе
async def about_me(current_user: Annotated[models.User, Depends(get_active_user)]):
    return current_user


@app.post("/change_user_data") #роут для создания пользователя
async def create_user(new_user: models.User,
                      current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_create = f"INSERT INTO users VALUES ({new_user.id}, '{new_user.username}', '{new_user.password}', '{new_user.role}')"


        return db_conn.query(qry_for_create)


    else:
        raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied",
                headers = {"WWW-Authenticate": "Bearer"}
            )


@app.put("/change_user_data") #роут для изменения роли пользователя
async def update_user_role(user_username: str, new_role: str, current_user: Annotated[
    models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_update = f"UPDATE users SET role = '{new_role}' WHERE username = '{user_username}'"


        return db_conn.query(qry_for_update)


    else:
        raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied",
                headers = {"WWW-Authenticate": "Bearer"}
            )


@app.delete("/change_user_data") #роут для удаления пользователя
async def delete_user(username: str, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_delete = f"DELETE FROM users WHERE username = '{username}'"


        return db_conn.query(qry_for_delete)


    else:
        raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied",
                headers = {"WWW-Authenticate": "Bearer"}
            )



@app.put("/photos") #роут для изменения фотки в БД
async def change_photo(pictures_name: models.ChangePictures,
                       current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        old_name = pictures_name.old_name
        new_name = pictures_name.new_name
        query_for_change = f"UPDATE photo SET path = '{PATH_PHOTO_GEOOBJECT}\{new_name}.jpg' WHERE path like '%\{old_name}.jpg%'"


        return db_conn.query(query_for_change)


    else:
        raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied",
                headers = {"WWW-Authenticate": "Bearer"}
            )


@app.delete("/photos") #роут для удаления фотки
async def delete_photo(picture_name: models.DeletePicture,
                       current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        delete_picture = picture_name.picture_name
        query_for_delete = f"DELETE FROM photo WHERE path = '{PATH_PHOTO_GEOOBJECT}\{delete_picture}.jpg'"


        return db_conn.query(query_for_delete)


    else:
        raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied",
                headers = {"WWW-Authenticate": "Bearer"}
            )




# Артура
@app.get("/geoobjects/{id_object}")
async def get_by_geoobject(id_object: UUID4):
    query = f"SELECT * FROM geoobject  WHERE id = '{id_object}'"

    result = db_conn.query(query, "one")

    res = Data_geoobjects(name=str(result[0]), description=str(result[1]), longitude=float(result[2]),
                          latitude=float(result[3]), id=str(result[4]),
                          type=str(result[5]), idgeopark=str(result[6]))

    return res


@app.get("/get_all_geoobject/")
async def get_all_geoobject():
    query1 = f"SELECT * FROM geoobject"

    result = db_conn.query(query1, "all")

    res = [GeoobjectModel(name=str(row[0]), description=str(row[1]), longitude=float(row[2]), latitude=float(row[3]),
                          id=str(row[4]),
                          type=str(row[5]), idgeopark=str(row[6])) for row in result]

    return res


@app.get("/get_all_geoobjects")
async def get_all_geoobjects(id_geopark: UUID4):
    query = f"SELECT geoobject.*, geopark.name FROM geoobject,geopark  WHERE geoobject.idgeopark = '{id_geopark}';"

    result = db_conn.query(query, "all")

    res = [GeoobjectModel(id=str(row[4]), name=str(row[0]), description=str(row[1]), longitude=float(row[2]),
                          latitude=float(row[3]), type=str(row[5]), idgeopark=str(row[6]), namegeopark=str(row[7])
                          ) for row in result]

    return res


@app.get("/get_photo_by_geoobject")
async def get_photo_by_geoobject(id_geoobject: UUID4):
    query1 = f"SELECT path FROM photo where geoobject_id = '{id_geoobject}';"

    result = db_conn.query(query1, "one")

    return {"path": str(result[0])}


@app.post("/create_photo_by_geoobject")
async def create_photo_by_geoobject(geoobject_id: UUID4, path_photo: str, preview_photo: bool):
    id = str(uuid.uuid4())

    path_photo = "/geopark_image/" + path_photo

    query = f"INSERT INTO photo(id,path,preview,geoobject_id) VALUES('{id}','{path_photo}','{preview_photo}','{geoobject_id}');"

    return db_conn.query(query, "")


@app.get("/aaa")  # хз как назвать его
async def photo_all(id_geoobject: UUID4):
    query1 = (
        f"SELECT geoobject.id, geoobject.name, geoobject.description, geoobject.longitude, geoobject.latitude, geoobject.type, geoobject.idgeopark, ARRAY_AGG(photo.path) as paths from geoobject"
        f" JOIN photo ON geoobject.id = photo.geoobject_id WHERE photo.geoobject_id = '{id_geoobject}'  AND photo.preview = '1' GROUP BY geoobject.id")

    result = db_conn.query(query1, "all")

    res = [GeoobjectPathModel(id=str(row[0]), name=str(row[1]), description=str(row[2]), longitude=float(row[3]),
                              latitude=float(row[4]), type=str(row[5]), idgeopark=str(row[6]), path_photo=str(row[len(row) - 1][0])) for row in result]
    return res


@app.get("/get_photo")
async def get_photos(id_geoobject: UUID4):
    query = f"SELECT path FROM photo WHERE geoobject_id = '{id_geoobject}'"

    result = db_conn.query(query, "all")

    res = [PathModel(path=str(row[0])) for row in result]

    return res
