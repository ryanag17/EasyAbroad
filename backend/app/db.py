import mysql.connector
from app.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_db_connection():
    return mysql.connector.connect(
        host=easyabroad-db,
        user=DB_USER,
        password=DB_PASSWORD,
        database=easy_abroad
    )
