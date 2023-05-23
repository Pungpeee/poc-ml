import datetime
from dotenv import load_dotenv
import psycopg2
import os
import json

class addData:
    def __init__(self, data):
        self.data = data
    
    def insertToDB(self):
        load_dotenv()
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT")
            )

            cursor = conn.cursor()
            print("Connection to db successful, adding data")
            cursor.execute("INSERT INTO logs (log,timestamp) VALUES (%s, %s)", (json.dumps(self.data),str(datetime.datetime.utcnow())))
            conn.commit()
            conn.close()
            print("Add log success")

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
