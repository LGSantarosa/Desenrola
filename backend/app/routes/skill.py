from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pymysql.connections import Connection
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/skills/me/save")
def save_skills(
    request: Request,
    teaches: List[int] = Form(default=[]),
    learns: List[int] = Form(default=[]),
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    with db.cursor() as cur:
        cur.execute("DELETE FROM user_skill WHERE user_id = %s", (user["id"],))

        for skill_id in set(teaches):
            cur.execute(
                "INSERT INTO user_skill (user_id, skill_id, type) VALUES (%s, %s, 'teaches')",
                (user["id"], skill_id),
            )
        for skill_id in set(learns):
            cur.execute(
                "INSERT INTO user_skill (user_id, skill_id, type) VALUES (%s, %s, 'learns')",
                (user["id"], skill_id),
            )
        db.commit()

    return RedirectResponse("/dashboard", status_code=303)
