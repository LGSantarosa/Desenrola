from fastapi import APIRouter, Depends, Query
from pymysql.connections import Connection
from typing import Optional
from app.core.database import get_db
from app.routes.user import get_current_user

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/")
def get_feed(
    category_id: Optional[int] = Query(None),
    user: dict = Depends(get_current_user),
    db: Connection = Depends(get_db),
):
    with db.cursor() as cur:
        cur.execute(
            "SELECT skill_id FROM user_skill WHERE user_id = %s AND type = 'teaches'",
            (user["id"],),
        )
        my_teach_ids = {r["skill_id"] for r in cur.fetchall()}

        cur.execute(
            "SELECT skill_id FROM user_skill WHERE user_id = %s AND type = 'learns'",
            (user["id"],),
        )
        my_learn_ids = {r["skill_id"] for r in cur.fetchall()}

        if category_id:
            cur.execute(
                """SELECT DISTINCT us.user_id FROM user_skill us
                   JOIN skill s ON s.id = us.skill_id
                   WHERE us.user_id != %s AND s.category_id = %s""",
                (user["id"], category_id),
            )
        else:
            cur.execute(
                "SELECT DISTINCT user_id FROM user_skill WHERE user_id != %s",
                (user["id"],),
            )
        user_ids = [r["user_id"] if "user_id" in r else r.get("user_id") for r in cur.fetchall()]

    results = []
    for uid in user_ids:
        with db.cursor() as cur:
            cur.execute("SELECT id, name, avatar FROM user WHERE id = %s", (uid,))
            other = cur.fetchone()
            if not other:
                continue

            cur.execute(
                """SELECT us.skill_id, s.id, s.name, us.type FROM user_skill us
                   JOIN skill s ON s.id = us.skill_id
                   WHERE us.user_id = %s""",
                (uid,),
            )
            rows = cur.fetchall()

        teach_skills = [{"id": r["id"], "name": r["name"]} for r in rows if r["type"] == "teaches"]
        learn_skills = [{"id": r["id"], "name": r["name"]} for r in rows if r["type"] == "learns"]

        their_teach_ids = {r["skill_id"] for r in rows if r["type"] == "teaches"}
        their_learn_ids = {r["skill_id"] for r in rows if r["type"] == "learns"}

        they_teach_i_want = my_learn_ids & their_teach_ids
        i_teach_they_want = my_teach_ids & their_learn_ids

        if they_teach_i_want and i_teach_they_want:
            score = 3
        elif they_teach_i_want:
            score = 2
        elif i_teach_they_want:
            score = 1
        else:
            score = 0

        results.append({
            "user": {
                "id": other["id"],
                "name": other["name"],
                "avatar": other["avatar"],
            },
            "teaches": teach_skills,
            "learns": learn_skills,
            "score": score,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
