import psycopg2
import environ


env = environ.Env()
environ.Env.read_env('.env')


def query(query: str):
    try:
        conn = psycopg2.connect(database=env('database'),
                            user=env('user'), 
                            password=env('password'),
                            host=env('host'), 
                            port=env('port')
        )
        cursor = conn.cursor()


        if query.split(" ")[0] == "INSERT":
            try:
                cursor.execute(query)
                conn.commit()
                return {"Succesfully created data"}

            except Exception as e:
                print(e)
                return {"Error"}
      

        elif query.split(" ")[0] == "SELECT":
            try:
                cursor.execute(query)
                data = cursor.fetchall()

                if data:
                    return data
                
                return False
            
            except Exception as e: 
                print(e)
                return {"Error"}


        elif query.split(" ")[0] == "UPDATE":
            try:
                cursor.execute(query)
                conn.commit()
                return {"Succesfully updated data"}

            except Exception as e:
                print(e)
                return {"Error"}
            

        elif query.split(" ")[0] == "DELETE":
            try:
                cursor.execute(query)
                conn.commit()
                return {"Successfully deleted data"}

            except Exception as e:
                print(e)
                return {"Error"}

              
        else:
            return {"Bad query"}


    except psycopg2.OperationalError as e:
        return {"Can\'t establish connection to database. Error:": e}


    finally:
        cursor.close()
        conn.close()