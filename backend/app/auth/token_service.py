from jose import jwt
import os
import datetime
import secrets
from app.config import JWT_SECRET, JWT_ALGORITHM

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def generate_reset_token():
    return secrets.token_hex(16)
