import psycopg2
from fastapi import Depends, FastAPI, HTTPException
# models.Base.metadata.create_all(bind=engine)
from config import DB_HOST,DB_PASS,DB_USER,DB_PORT,DB_NAME,PATH_PHOTO_GEOOBJECT
import models
import db_conn
conn_params = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}

app = FastAPI()

@app.get("/geoparks")
async def get_data_about_geopark():
    try:
        connection = psycopg2.connect(**conn_params)
        cursor = connection.cursor()

        query = "SELECT * FROM geopark"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        return {"data": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/geoobjects")
async def get_data_about_geobject(long: float):
    try:
        connection = psycopg2.connect(**conn_params)
        cursor = connection.cursor()

        query = f"SELECT * FROM geoobject WHERE longitude = '{long}'"
        cursor.execute(query)
        print(query)
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        return {"data": result}
    except Exception as e:
        return {"error": str(e)}
    

@app.put("/photos")
async def change_photo(pictures_name: models.ChangePictures):
    old_name = pictures_name.old_name
    new_name = pictures_name.new_name
    query_for_change = f"UPDATE photo SET path = '{PATH_PHOTO_GEOOBJECT}\{new_name}.jpg' WHERE path like '%\{old_name}.jpg%'"
    return db_conn.query(query_for_change)


@app.delete("/photos")
async def delete_photo(picture_name: models.DeletePicture):
    delete_picture = picture_name.picture_name
    query_for_delete = f"DELETE FROM photo WHERE path = '{PATH_PHOTO_GEOOBJECT}\{delete_picture}.jpg'"
    return db_conn.query(query_for_delete)
