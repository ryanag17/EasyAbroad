from jose import jwt
from datetime import datetime, timedelta
import secrets
from app.config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    # 10-year expiry
    expire = datetime.utcnow() + timedelta(days=365 * 10)
    to_encode.update({"exp": expire})
    # Use settings for secret & algorithm
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

def generate_reset_token():
    return secrets.token_hex(16)
