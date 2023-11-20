from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import jwt, JWTError
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import models
import db_conn
from config import DB_HOST, DB_PASS, DB_USER, DB_PORT, DB_NAME, PATH_PHOTO_GEOOBJECT
from pydantic import UUID4

import uuid


conn_params = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}


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


SECRET_KEY = "oPP6V7pbQsL5XYKI7HfXZQs2hp42fU96"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):  # создание токена
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_user(username: str):  # получение информации о пользователе из БД
    qry_username = f"SELECT * FROM users WHERE username = '{username}'"
    qry_username_result = db_conn.query(qry_username)

    user = models.User(
        id=int(qry_username_result[0][0]),
        username=qry_username_result[0][1],
        password=qry_username_result[0][2],
        role=qry_username_result[0][3],
    )

    dict_for_user = {
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }

    return dict_for_user


def get_user_from_token(
        token: Annotated[str, Depends(oauth2_scheme)]):  # получение пользователя из полезной нагрузки токена
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = models.TokenData(username=username)


    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


def get_active_user(user_from_token: Annotated[models.User, Depends(
    get_user_from_token)]):  # получение пользователя (декоратор для user from token)
    return user_from_token


def get_user_from_db(username: str,
                     password: str):  # получение айдишника пользователя из бд для проверки наличия пользователя
    id_query = f"SELECT id FROM users WHERE username = '{username}' and password = '{password}'"
    id_from_db = db_conn.query(id_query)[0][0]

    if id_from_db:
        return True

    return False


@app.get("/user", tags=['user']) # TEST ROUTE
async def test():
    q = f"SELECT * FROM users"
    return db_conn.query(q)


@app.post("/login", tags=['auth'])  # роут для аутентификации
async def auth(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_from_db = get_user_from_db(form_data.username, form_data.password)


    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )


    user = get_user(form_data.username)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


    token = create_jwt_token(
        data = {"id": user["id"],
                "sub": user["username"],
                "role": user["role"]}, 
        expires_delta=access_token_expires
    )


    return {"token": token}


@app.get("/about_me", response_model=models.User, tags=['auth'])  # роут для проверки авторизации - выводит информацию о пользователе
async def about_me(current_user: Annotated[models.User, Depends(get_active_user)]):
    return current_user


@app.post("/user", tags=['user'])  # роут для создания пользователя
async def create_user(new_user: models.User,
                      current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_create = f"INSERT INTO users VALUES ({new_user.id}, '{new_user.username}', '{new_user.password}', '{new_user.role}')"

        return db_conn.query(qry_for_create)


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.put("/user", tags=['user'])  # роут для изменения роли пользователя
async def update_user_role(user_username: str, new_role: str,
                           current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_update = f"UPDATE users SET role = '{new_role}' WHERE username = '{user_username}'"

        return db_conn.query(qry_for_update)


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.delete("/user", tags=['user'])  # роут для удаления пользователя
async def delete_user(username: str, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        qry_for_delete = f"DELETE FROM users WHERE username = '{username}'"

        return db_conn.query(qry_for_delete)


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.put("/photo", tags=['photo'])  # роут для изменения фотки в БД
async def change_photo(pictures_name: models.ChangePictures,
                       current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        old_name = pictures_name.old_name
        new_name = pictures_name.new_name
        query_for_change = f"UPDATE photo SET path = '{PATH_PHOTO_GEOOBJECT}\{new_name}.jpg' WHERE path like '%\{old_name}.jpg%'"

        return db_conn.query(query_for_change)


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.delete("/photo", tags=['photo'])  # роут для удаления фотки
async def delete_photo(picture_name: models.DeletePicture,
                       current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        delete_picture = picture_name.picture_name
        query_for_delete = f"DELETE FROM photo WHERE path = '{PATH_PHOTO_GEOOBJECT}\{delete_picture}.jpg'"

        return db_conn.query(query_for_delete)


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.get("/geoobject/{id}", tags=['geoobject'], response_model=models.GeoobjectModel)
async def get_geoobject(id: UUID4):
    query = f"SELECT * FROM geoobject  WHERE id = '{id}'"
    result = db_conn.query(query)
    result = result[0]
    res =  models.GeoobjectModel(
        name=str(result[0]),
        description=str(result[1]),
        longitude=float(result[2]),
        latitude=float(result[3]),
        id=str(result[4]),
        type=str(result[5]),
        geoparkId=str(result[6]))
    return res

@app.get("/geoobject_geopark/{geopark_id}", tags=['geoobject'], response_model=List[models.GeoobjectModel])
async def get_geoobjects_by_geopark(geopark_id: str):
    query = f"SELECT geoobject.* FROM geoobject  WHERE geoobject.idgeopark = '{geopark_id}';"
    result = db_conn.query(query)
    res = [
        models.GeoobjectModel(
            id=str(row[4]),
            name=str(row[0]),
            description=str(row[1]),
            longitude=float(row[2]),
            latitude=float(row[3]),
            type=str(row[5]),
            geoparkId=str(row[6]))
        for row in result
    ]
    return res
@app.get("/geoobject", tags=['geoobject'], response_model=List[models.GeoobjectModel])
async def get_all_geobjects():
    query1 = f"SELECT * FROM geoobject"
    result = db_conn.query(query1)
    res = [models.GeoobjectModel(
        name=str(row[0]),
        description=str(row[1]),
        longitude=float(row[2]),
        latitude=float(row[3]),
        id=str(row[4]),
        type=str(row[5]),
        geoparkId=str(row[6]))
        for row in result]
    return res


@app.post("/photo", tags=['photo'])
async def add_photo_by_id_geoobject(geoobject_id: UUID4, path_photo: str, preview_photo: bool, file: UploadFile):
    # id = str(uuid.uuid4())
    # path_photo = "/geopark_image/" + path_photo
    # query = f"INSERT INTO photo(id,path,preview,geoobject_id) VALUES('{id}','{path_photo}','{preview_photo}','{geoobject_id}');"

    # return db_conn.query(query)
    return file

@app.get("/geoobject_detail/{id}", tags=['geoobject'], response_model=models.GeoobjectModelDetail)
async def get_geoobject_and_photos(id: UUID4):
    query = (
        f"SELECT geoobject.id, geoobject.name, geoobject.description, geoobject.longitude, geoobject.latitude, geoobject.type, geoobject.idgeopark, ARRAY_AGG(photo.path) as paths from geoobject"
        f" JOIN photo ON geoobject.id = photo.geoobject_id WHERE photo.geoobject_id = '{id}' GROUP BY geoobject.id")

    query_result = db_conn.query(query)
    result = query_result[0]


    res = models.GeoobjectModelDetail(
            id=str(result[0]),
            name=str(result[1]),
            description=str(result[2]),
            longitude=float(result[3]),
            latitude=float(result[4]), type=str(result[5]),
            geoparkId=str(result[6]),
            photoPaths=list(result[len(result) - 1])
        )
    return res

@app.get("/photos_geoobject{geoobject_id}", tags=['photo'])
async def photos_by_geoobject(geoobject_id: UUID4):
    query = f"SELECT photo.* FROM photo WHERE geoobject_id = '{geoobject_id}'"
    result = db_conn.query(query)

    res = [models.PhotoModel(
        path=str(row[0]),
        id=str(row[2]),
        geoobjectId=str(row[1]),
        preview=bool(row[3])
    ) for row in result]

    return res


@app.get("/geopark", tags=['geopark'], response_model=List[models.GeoparkModel])
async def get_geoparks():
    query = f"SELECT geopark.* FROM geopark"
    result = db_conn.query(query)

    res = [models.GeoparkModel(
        id=str(row[0]),
        name=str(row[1]),
        latitude=float(row[2]),
        longitude=float(row[3]),
        description=str(row[4])
    ) for row in result]
    return res


@app.put("/geoobject", tags=['geoobject'])
async def update_geoobject(id: UUID4, new_data: models.UpdateGeoobjectModel, 
                           current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        update_query = f"UPDATE geoobject SET "


        if new_data.name:
            update_query += f"name = '{new_data.name}',"


        elif new_data.description:
            update_query += f"description = '{new_data.description}',"


        elif new_data.longitude:
            update_query += f"longitude = {new_data.longitude},"


        elif new_data.latitude:
            update_query += f"latitude = {new_data.latitude},"


        elif new_data.type:
            update_query += f"type = '{new_data.type}',"


        elif new_data.geoparkId:
            update_query += f"geoparkId = '{new_data.geoparkId}',"


        else:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields are empty"
        )

        
        update_query = update_query[:-1] + f" "
        update_query = update_query + f"WHERE id = '{id}'"
            
        
       # return update_query коммент не убирать
        return db_conn.query(update_query)
    
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@app.post("/geoobject", tags=['geoobject'])
async def create_geoobject(new_geoobject: models.GeoobjectModel,
                           current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        if new_geoobject.name and new_geoobject.longitude and new_geoobject.latitude and new_geoobject.id and new_geoobject.type and new_geoobject.geoparkId:
            create_query = f"INSERT INTO geoobject VALUES ('{new_geoobject.name}', '{new_geoobject.description}', {new_geoobject.longitude}, {new_geoobject.latitude}, '{new_geoobject.id}', '{new_geoobject.type}', '{new_geoobject.geoparkId}')"


            return db_conn.query(create_query)
        

        else:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="some fields are empty"
        )

    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

@app.delete("/geoobject", tags=['geoobject'])
async def delete_geoobject(id: UUID4, current_user: Annotated[models.User, Depends(get_active_user)]):
    if current_user and current_user["role"] == "admin":
        delete_query = f"DELETE FROM geoobject WHERE id = '{id}'"


        return db_conn.query(delete_query)
    

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"}
        )