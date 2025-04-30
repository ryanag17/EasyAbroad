from fastapi import HTTPException
from app.db import get_db_connection
import bcrypt
import datetime
from app.auth.token_service import create_access_token, generate_reset_token
from app.auth.models import UserLogin, UserCreate, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.email_service import send_reset_email



def register(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (name, surname, role, email, password) VALUES (%s, %s, %s, %s, %s)",
        (user.name, user.surname, user.role, user.email, hashed_pw.decode('utf-8'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User registered successfully"}

def login(user: UserLogin):
    user_in_db = get_user_by_email(user.email)
    if not user_in_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, user_in_db["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def forgot_password(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    token = generate_reset_token()
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    cursor.execute("UPDATE users SET reset_token = %s, token_expiry = %s WHERE email = %s", (token, expiry, email))
    conn.commit()
    cursor.close()
    conn.close()
    send_reset_email(email, token)
    return {"message": "Reset email sent if the address exists."}

def reset_password(token, new_password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE reset_token = %s", (token,))
    user = cursor.fetchone()
    if not user or user['token_expiry'] < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = %s, reset_token = NULL, token_expiry = NULL WHERE id = %s",
        (hashed_pw.decode('utf-8'), user['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Password reset successfully"}
