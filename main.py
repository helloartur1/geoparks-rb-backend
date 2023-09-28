import psycopg2
from fastapi import Depends, FastAPI, HTTPException
# models.Base.metadata.create_all(bind=engine)
from config import DB_HOST,DB_PASS,DB_USER,DB_PORT,DB_NAME
import psycopg
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