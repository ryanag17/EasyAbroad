import mysql.connector
from app.config import settings

def get_db_connection():
    """
    Returns a new MySQL connection using the
    settings from app/config.py (which pulls from your .env).
    """
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )