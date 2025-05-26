# ── Force-load environment variables before anything else ──
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os

DB_HOST     = os.getenv("DB_HOST")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME     = os.getenv("DB_NAME")

# These will now definitely be populated from your .env
JWT_SECRET     = os.getenv("JWT_SECRET")
JWT_ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")
