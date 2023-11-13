import psycopg2


def query(query: str, type: str):
    try:
        conn = psycopg2.connect(database='postgres',
                                user='postgres',
                                password='123',
                                host='localhost',
                                port='5432')
        cursor = conn.cursor()

        if query.split(" ")[0] == "INSERT":

            try:
                cursor.execute(query)
                conn.commit()
                return {"Succesfully created data "}


            except Exception as e:
                print(e)
                return {"Error"}



        elif query.split(" ")[0] == "SELECT" and type == "all":

            try:
                cursor.execute(query)
                data = cursor.fetchall()
                print(data)
                if data:
                    return data
                return {404}
            except Exception as e:
                print(e)
                return {"Error"}

        elif query.split(" ")[0] == "SELECT" and type == "one":
            try:
                cursor.execute(query)
                return  cursor.fetchone()

            except Exception as e:
                print(e)
                return {"Error"}





        elif query.split(" ")[0] == "UPDATE":

            try:
                cursor.execute(query)
                conn.commit()
                return {"Succesfully updated data"}


            except Exception as e:
                print(111)
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