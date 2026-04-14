from fastapi import APIRouter, Depends, HTTPException, Header
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import hash_password, decode_token
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(authorization: str = Header(...), db: Connection = Depends(get_db)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        with db.cursor() as cur:
            cur.execute("SELECT * FROM user WHERE id = %s", (payload["user_id"],))
            user = cur.fetchone()
        if not user:
            raise HTTPException(401, "Usuario nao encontrado")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(401, "Token invalido")


@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "cpf": user["cpf"],
        "phone": user["phone"],
        "birth_date": str(user["birth_date"]),
        "role": user["role"],
        "avatar": user["avatar"],
    }


@router.put("/me")
def update_me(data: UserUpdate, user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    updates = []
    params = []

    if data.name is not None:
        updates.append("name = %s")
        params.append(data.name)
    if data.email is not None:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM user WHERE email = %s AND id != %s", (data.email, user["id"]))
            if cur.fetchone():
                raise HTTPException(400, "Email ja cadastrado")
        updates.append("email = %s")
        params.append(data.email)
    if data.password is not None:
        updates.append("password = %s")
        params.append(hash_password(data.password))
    if data.cpf is not None:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM user WHERE cpf = %s AND id != %s", (data.cpf, user["id"]))
            if cur.fetchone():
                raise HTTPException(400, "CPF ja cadastrado")
        updates.append("cpf = %s")
        params.append(data.cpf)
    if data.phone is not None:
        updates.append("phone = %s")
        params.append(data.phone)
    if data.birth_date is not None:
        updates.append("birth_date = %s")
        params.append(data.birth_date)

    if not updates:
        return user

    params.append(user["id"])
    with db.cursor() as cur:
        cur.execute(f"UPDATE user SET {', '.join(updates)} WHERE id = %s", params)
        db.commit()
        cur.execute("SELECT * FROM user WHERE id = %s", (user["id"],))
        updated = cur.fetchone()

    return {
        "id": updated["id"],
        "name": updated["name"],
        "email": updated["email"],
        "cpf": updated["cpf"],
        "phone": updated["phone"],
        "birth_date": str(updated["birth_date"]),
        "role": updated["role"],
        "avatar": updated["avatar"],
    }


@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, avatar, role FROM user WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(404, "Usuario nao encontrado")

        cur.execute(
            """SELECT us.type, s.name FROM user_skill us
               JOIN skill s ON s.id = us.skill_id
               WHERE us.user_id = %s""",
            (user_id,),
        )
        rows = cur.fetchall()

    teaches = [r["name"] for r in rows if r["type"] == "teaches"]
    learns = [r["name"] for r in rows if r["type"] == "learns"]

    return {
        "id": user["id"],
        "name": user["name"],
        "avatar": user["avatar"],
        "role": user["role"],
        "teaches": teaches,
        "learns": learns,
    }


@router.delete("/me")
def delete_me(user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("DELETE FROM user WHERE id = %s", (user["id"],))
        db.commit()
    return {"message": "Conta deletada"}
