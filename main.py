from pydantic import UUID4, BaseModel
import psycopg2
import uuid
from fastapi import Depends, FastAPI, HTTPException
# models.Base.metadata.create_all(bind=engine)
import db_conn
from config import DB_HOST,DB_PASS,DB_USER,DB_PORT,DB_NAME
conn_params = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}

app = FastAPI()

class Data_geoobjects(BaseModel):
    id : str
    name : str
    description : str
    longitude : float
    latitude : float
    type : str
    idgeopark : str



@app.get("/geoobjects/{id_object}")
async def get_geoobject_via_id(id_object : UUID4):
    query = f"SELECT * FROM geoobject  WHERE id = '{id_object}'"
    result = db_conn.query(query,"one")
    res = Data_geoobjects(name=str(result[0]), description = str(result[1]), longitude = float(result[2]), latitude = float(result[3]), id = str(result[4]),
                type = str(result[5]),idgeopark = str(result[6]))
    return res


@app.get("/geoobjects/")
async def get_data_about_geobjects():
    query1 = f"SELECT * FROM geoobject"
    result = db_conn.query(query1,"all")
    i1= [Data_geoobjects(name=str(row[0]), description = str(row[1]), longitude = float(row[2]), latitude = float(row[3]), id = str(row[4]),
                  type = str(row[5]),idgeopark = str(row[6])) for row in result ]
    return i1

class Geoobject_by_geopark(BaseModel):
    id : str
    name : str
    description : str
    longitude : float
    latitude : float
    type : str
    idgeopark : str
    namegeopark : str
@app.get("/geoobjectsbyidpark")
async def get_all_222(id_geopark : UUID4):
    query = f"SELECT geoobject.*, geopark.name FROM geoobject,geopark  WHERE geoobject.idgeopark = '{id_geopark}';"
    result = db_conn.query(query,"all")
    res = [Geoobject_by_geopark(id=str(row[4]), name=str(row[0]), description=str(row[1]), longitude=float(row[2]),
              latitude=float(row[3]), type=str(row[5]), idgeopark = str(row[6]), namegeopark = str(row[7])
              ) for row in result]
    return res

@app.get("/photo_by_geoobjectid")
async def photo(id_geopark: UUID4):
    query1 = f"SELECT path FROM photo where geopark_id = '{id_geopark}';"
    result = db_conn.query(query1,"one")
    return {"path":str(result[0])}

@app.post("/add_photo")
async def add_photo_by_id_geoobject(geoobject_id : UUID4, path_photo : str,preview_photo :bool):
    id=str(uuid.uuid4())
    path_photo = "/geopark_image/" + path_photo
    query = f"INSERT INTO photo(id,path,preview,geoobject_id) VALUES('{id}','{path_photo}','{preview_photo}','{geoobject_id}');"

    return db_conn.query(query,"")

class Data_geoobjects_with_photo(BaseModel):
    id : str
    name : str
    description : str
    longitude : float
    latitude : float
    type : str
    idgeopark : str
    path_photo : str


@app.get("/aaa")
async def photo_all(id_geoobject: UUID4):
    query1 = (f"SELECT geoobject.id, geoobject.name, geoobject.description, geoobject.longitude, geoobject.latitude, geoobject.type, geoobject.idgeopark, ARRAY_AGG(photo.path) as paths from geoobject"
              f" JOIN photo ON geoobject.id = photo.geoobject_id WHERE photo.geoobject_id = '{id_geoobject}'  AND photo.preview = '1' GROUP BY geoobject.id")

    result = db_conn.query(query1,"all")

    res = [Data_geoobjects_with_photo(id=str(row[0]), name=str(row[1]), description=str(row[2]), longitude=float(row[3]),
                                latitude=float(row[4]), type=str(row[5]), idgeopark=str(row[6]), path_photo = str(row[len(row) - 1][0]
)
                                ) for row in result]

    print(result)
    return res

class Paths(BaseModel):
    path : str
@app.get("/get_photo")
async def photos(id_geoobject: UUID4):
    query = f"SELECT path FROM photo WHERE geoobject_id = '{id_geoobject}'"
    result = db_conn.query(query,"all")

    res = [Paths(path = str(row[0])) for row in result]

    return res

#
# @app.put("/update_photo/")
# async def update_photo(id_geoobject:UUID4, new_path : str, id_changed_photo : UUID4):
#     query = f"Update  photo SET path = '{new_path}' WHERE geoobject_id = '{id_geoobject}' AND id = '{id_changed_photo}'"
#
#     return db_conn.query(query,"all")