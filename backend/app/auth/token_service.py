from jose import jwt
import os
from datetime import datetime, timedelta
import secrets
from app.config import JWT_SECRET, JWT_ALGORITHM

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=365*10)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_reset_token():
    return secrets.token_hex(16)
