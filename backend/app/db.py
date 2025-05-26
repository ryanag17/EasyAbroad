import mysql.connector
from app.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_db_connection():
    """
    Returns a new MySQL connection using the
    settings from app/config.py (which pulls from your .env).
    """
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
