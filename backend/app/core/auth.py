import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Request, Depends
from app.core.database import get_db

load_dotenv()

SECRET = os.getenv("JWT_SECRET")
COOKIE_NAME = "session"
COOKIE_MAX_AGE = 30 * 60 #tempo maximo do cookie de autent (30 min, renovado a cada request)


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=COOKIE_MAX_AGE),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])


def set_auth_cookie(response, token):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )


def clear_auth_cookie(response):
    response.delete_cookie(COOKIE_NAME, path="/")


def get_current_user(request: Request, db=Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        payload = decode_token(token)
    except Exception:
        return None
    with db.cursor() as cur:
        cur.execute("SELECT * FROM user WHERE id = %s", (payload["user_id"],))
        return cur.fetchone()
