from fastapi import APIRouter, Depends, HTTPException
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_token
from app.schemas.user import UserCreate, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(data: UserCreate, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id FROM user WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(400, "Email ja cadastrado")

        cur.execute("SELECT id FROM user WHERE cpf = %s", (data.cpf,))
        if cur.fetchone():
            raise HTTPException(400, "CPF ja cadastrado")

        cur.execute(
            """INSERT INTO user (name, email, password, cpf, phone, birth_date)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (data.name, data.email, hash_password(data.password),
             data.cpf, data.phone, data.birth_date),
        )
        db.commit()
        user_id = cur.lastrowid

        cur.execute("SELECT id, name, role FROM user WHERE id = %s", (user_id,))
        user = cur.fetchone()

    token = create_token(user["id"], user["role"])
    return {"token": token, "user": {"id": user["id"], "name": user["name"], "role": user["role"]}}


@router.post("/login")
def login(data: LoginRequest, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, password, role FROM user WHERE email = %s", (data.email,))
        user = cur.fetchone()

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Email ou senha incorretos")

    token = create_token(user["id"], user["role"])
    return {"token": token, "user": {"id": user["id"], "name": user["name"], "role": user["role"]}}
