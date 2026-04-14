from fastapi import APIRouter, Depends
from pymysql.connections import Connection
from app.core.database import get_db
from app.routes.user import get_current_user

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/")
def find_matches(user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
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

    if not my_teach_ids or not my_learn_ids:
        return []

    with db.cursor() as cur:
        placeholders = ",".join(["%s"] * len(my_learn_ids))
        cur.execute(
            f"""SELECT DISTINCT user_id FROM user_skill
                WHERE user_id != %s AND type = 'teaches' AND skill_id IN ({placeholders})""",
            [user["id"]] + list(my_learn_ids),
        )
        candidate_ids = [r["user_id"] for r in cur.fetchall()]

    matches = []
    for cid in candidate_ids:
        with db.cursor() as cur:
            cur.execute(
                "SELECT skill_id FROM user_skill WHERE user_id = %s AND type = 'teaches'",
                (cid,),
            )
            their_teach_ids = {r["skill_id"] for r in cur.fetchall()}

            cur.execute(
                "SELECT skill_id FROM user_skill WHERE user_id = %s AND type = 'learns'",
                (cid,),
            )
            their_learn_ids = {r["skill_id"] for r in cur.fetchall()}

        they_teach_i_want = my_learn_ids & their_teach_ids
        i_teach_they_want = my_teach_ids & their_learn_ids

        if they_teach_i_want and i_teach_they_want:
            with db.cursor() as cur:
                cur.execute("SELECT id, name, avatar FROM user WHERE id = %s", (cid,))
                candidate_user = cur.fetchone()

                def get_skill_names(ids):
                    if not ids:
                        return []
                    ph = ",".join(["%s"] * len(ids))
                    cur.execute(f"SELECT name FROM skill WHERE id IN ({ph})", list(ids))
                    return [r["name"] for r in cur.fetchall()]

                matches.append({
                    "user": {
                        "id": candidate_user["id"],
                        "name": candidate_user["name"],
                        "avatar": candidate_user["avatar"],
                    },
                    "they_teach": get_skill_names(they_teach_i_want),
                    "they_want": get_skill_names(i_teach_they_want),
                })

    return matches
