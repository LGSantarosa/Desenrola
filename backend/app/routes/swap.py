from fastapi import APIRouter, Depends, HTTPException
from pymysql.connections import Connection
from app.core.database import get_db
from app.routes.user import get_current_user

router = APIRouter(prefix="/swaps", tags=["swaps"])


@router.post("/")
def create_swap(receiver_id: int, offered_skill_id: int, desired_skill_id: int,
                user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    if receiver_id == user["id"]:
        raise HTTPException(400, "Nao pode enviar troca pra voce mesmo")

    with db.cursor() as cur:
        cur.execute("SELECT id FROM user WHERE id = %s", (receiver_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Usuario nao encontrado")

        cur.execute(
            """SELECT id FROM swap_request
               WHERE sender_id = %s AND receiver_id = %s AND status = 'pending'""",
            (user["id"], receiver_id),
        )
        if cur.fetchone():
            raise HTTPException(400, "Ja existe uma solicitacao pendente")

        cur.execute(
            """INSERT INTO swap_request (sender_id, receiver_id, offered_skill_id, desired_skill_id)
               VALUES (%s, %s, %s, %s)""",
            (user["id"], receiver_id, offered_skill_id, desired_skill_id),
        )
        db.commit()
    return {"message": "Solicitacao enviada"}


@router.get("/received")
def received_swaps(user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM swap_request WHERE receiver_id = %s", (user["id"],))
        swaps = cur.fetchall()
    return [format_swap(s, db) for s in swaps]


@router.get("/sent")
def sent_swaps(user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM swap_request WHERE sender_id = %s", (user["id"],))
        swaps = cur.fetchall()
    return [format_swap(s, db) for s in swaps]


@router.put("/{swap_id}")
def update_swap(swap_id: int, status: str, user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    if status not in ("accepted", "rejected"):
        raise HTTPException(400, "Status deve ser 'accepted' ou 'rejected'")

    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM swap_request WHERE id = %s AND receiver_id = %s",
            (swap_id, user["id"]),
        )
        swap = cur.fetchone()
        if not swap:
            raise HTTPException(404, "Solicitacao nao encontrada")

        if swap["status"] != "pending":
            raise HTTPException(400, "Solicitacao ja foi respondida")

        cur.execute("UPDATE swap_request SET status = %s WHERE id = %s", (status, swap_id))
        db.commit()
    return {"message": "Solicitacao " + ("aceita" if status == "accepted" else "recusada")}


def format_swap(s, db):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, avatar, email, phone FROM user WHERE id = %s", (s["sender_id"],))
        sender = cur.fetchone()
        cur.execute("SELECT id, name, avatar, email, phone FROM user WHERE id = %s", (s["receiver_id"],))
        receiver = cur.fetchone()
        cur.execute("SELECT name FROM skill WHERE id = %s", (s["offered_skill_id"],))
        offered = cur.fetchone()
        cur.execute("SELECT name FROM skill WHERE id = %s", (s["desired_skill_id"],))
        desired = cur.fetchone()

    result = {
        "id": s["id"],
        "status": s["status"],
        "created_at": str(s["created_at"]),
        "sender": {"id": sender["id"], "name": sender["name"], "avatar": sender["avatar"]},
        "receiver": {"id": receiver["id"], "name": receiver["name"], "avatar": receiver["avatar"]},
        "offered_skill": offered["name"],
        "desired_skill": desired["name"],
    }
    if s["status"] == "accepted":
        result["sender"]["email"] = sender["email"]
        result["sender"]["phone"] = sender["phone"]
        result["receiver"]["email"] = receiver["email"]
        result["receiver"]["phone"] = receiver["phone"]
    return result
