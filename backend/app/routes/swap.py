from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/swaps/create")
def create_swap(
    request: Request,
    receiver_id: int = Form(...),
    offered_skill_id: int = Form(...),
    desired_skill_id: int = Form(...),
    redirect_to: str = Form("/dashboard"),
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    if receiver_id == user["id"]:
        return RedirectResponse(redirect_to, status_code=303)

    with db.cursor() as cur:
        cur.execute("SELECT id FROM user WHERE id = %s", (receiver_id,))
        if not cur.fetchone():
            return RedirectResponse(redirect_to, status_code=303)

        cur.execute(
            """SELECT id FROM swap_request
               WHERE sender_id = %s AND receiver_id = %s AND status = 'pending'""",
            (user["id"], receiver_id),
        )
        if cur.fetchone():
            return RedirectResponse(redirect_to + "?swap=duplicate", status_code=303)

        cur.execute(
            """INSERT INTO swap_request (sender_id, receiver_id, offered_skill_id, desired_skill_id)
               VALUES (%s, %s, %s, %s)""",
            (user["id"], receiver_id, offered_skill_id, desired_skill_id),
        )
        db.commit()

    return RedirectResponse(redirect_to + "?swap=sent", status_code=303)


@router.post("/swaps/{swap_id}/accept")
def accept_swap(swap_id: int, request: Request, db: Connection = Depends(get_db)):
    return _update_status(swap_id, "accepted", request, db)


@router.post("/swaps/{swap_id}/reject")
def reject_swap(swap_id: int, request: Request, db: Connection = Depends(get_db)):
    return _update_status(swap_id, "rejected", request, db)


def _update_status(swap_id, status, request, db):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    with db.cursor() as cur:
        cur.execute(
            "SELECT status FROM swap_request WHERE id = %s AND receiver_id = %s",
            (swap_id, user["id"]),
        )
        swap = cur.fetchone()
        if swap and swap["status"] == "pending":
            cur.execute("UPDATE swap_request SET status = %s WHERE id = %s", (status, swap_id))
            db.commit()

    return RedirectResponse("/swaps", status_code=303)
