from fastapi import HTTPException
from app.db import get_db_connection
import bcrypt
import datetime
from app.auth.token_service import create_access_token, generate_reset_token
from app.auth.models import UserLogin, UserCreate
from app.auth.email_service import send_reset_email


def register(user: UserCreate):
    """
    1) Insert new user into users
    2) If role == "student", immediately seed a row in students
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # hash the password
        hashed_pw = bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # 1) create users row
        cursor.execute(
            """
            INSERT INTO users
              (first_name, last_name, email, password_hash, role, city, country, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
            (
                user.name,
                user.surname,
                user.email,
                hashed_pw,
                user.role,
                "",   # city
                ""    # country
            )
        )

        new_user_id = cursor.lastrowid

        # 2) if student, seed students table with optional birthday
        if user.role.lower() == "student":
            cursor.execute(
                "INSERT INTO students (user_id) VALUES (%s)",
                (new_user_id,)
            )

        conn.commit()
        return {"message": "User registered successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()
        conn.close()


def login(user: UserLogin):
    """
    Authenticate and issue JWT.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, password_hash, role FROM users WHERE email = %s",
        (user.email,)
    )
    db_user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(
        user.password.encode("utf-8"),
        db_user["password_hash"].encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_payload = {"sub": db_user["id"], "role": db_user["role"]}
    access_token = create_access_token(token_payload)

    return {"access_token": access_token, "token_type": "bearer"}


def forgot_password(email: str):
    """
    Generate a reset token, store it and its expiry, send email.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    token = generate_reset_token()
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    cursor.execute(
        "UPDATE users SET reset_token = %s, token_expiry = %s WHERE email = %s",
        (token, expiry, email)
    )
    conn.commit()
    cursor.close()
    conn.close()

    send_reset_email(email, token)
    return {"message": "Reset email sent if the address exists."}


def reset_password(token: str, new_password: str):
    """
    Validate reset token + expiry, update password, clear token fields.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, token_expiry FROM users WHERE reset_token = %s",
        (token,)
    )
    user = cursor.fetchone()

    if not user or user["token_expiry"] < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    cursor.execute(
        """
        UPDATE users
           SET password_hash = %s,
               reset_token = NULL,
               token_expiry = NULL
         WHERE id = %s
        """,
        (hashed_pw.decode("utf-8"), user["id"])
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Password reset successfully"}


def get_student_profile(user_id: int):
    """
    Fetch joined data from users + students for GET /students/me
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
          u.first_name, u.last_name, u.email,
          u.city, u.country,
          s.birthday, s.gender, s.languages, s.profile_picture
        FROM users AS u
        LEFT JOIN students AS s ON u.id = s.user_id
        WHERE u.id = %s
        """,
        (user_id,)
    )
    profile = cursor.fetchone()
    cursor.close()
    conn.close()

    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    return profile


def update_student_profile(user_id: int, data: dict):
    """
    Update users and students tables based on provided fields.
    Ensures a students row always exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1) Update users table fields (including email)
    user_fields, user_vals = [], []
    for col in ("first_name", "last_name", "email", "city", "country"):
        if col in data:
            user_fields.append(f"{col} = %s")
            user_vals.append(data[col])

    if user_fields:
        cursor.execute(
            f"UPDATE users SET {', '.join(user_fields)} WHERE id = %s",
            (*user_vals, user_id)
        )

    # 2) Ensure a students row exists
    cursor.execute(
        "SELECT 1 FROM students WHERE user_id = %s",
        (user_id,)
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO students (user_id) VALUES (%s)",
            (user_id,)
        )

    # 3) Update students-specific fields
    stud_fields, stud_vals = [], []
    for col in ("birthday", "gender", "languages", "profile_picture"):
        if col in data:
            stud_fields.append(f"{col} = %s")
            stud_vals.append(data[col])

    if stud_fields:
        cursor.execute(
            f"UPDATE students SET {', '.join(stud_fields)} WHERE user_id = %s",
            (*stud_vals, user_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return True
