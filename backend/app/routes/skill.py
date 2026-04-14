from fastapi import APIRouter, Depends, HTTPException
from pymysql.connections import Connection
from app.core.database import get_db
from app.routes.user import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/categories")
def list_categories(db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name FROM category ORDER BY name")
        cats = cur.fetchall()

        result = []
        for cat in cats:
            cur.execute(
                "SELECT id, name FROM skill WHERE category_id = %s ORDER BY name",
                (cat["id"],),
            )
            skills = cur.fetchall()
            result.append({
                "id": cat["id"],
                "name": cat["name"],
                "skills": [{"id": s["id"], "name": s["name"]} for s in skills],
            })
    return result


@router.get("/me")
def my_skills(user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            """SELECT us.id, us.type, s.id AS skill_id, s.name
               FROM user_skill us JOIN skill s ON s.id = us.skill_id
               WHERE us.user_id = %s""",
            (user["id"],),
        )
        rows = cur.fetchall()

    teaches = [{"id": r["id"], "skill_id": r["skill_id"], "name": r["name"]}
               for r in rows if r["type"] == "teaches"]
    learns = [{"id": r["id"], "skill_id": r["skill_id"], "name": r["name"]}
              for r in rows if r["type"] == "learns"]
    return {"teaches": teaches, "learns": learns}


@router.post("/me")
def add_skill(skill_id: int, type: str, user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    if type not in ("teaches", "learns"):
        raise HTTPException(400, "Tipo deve ser 'teaches' ou 'learns'")

    with db.cursor() as cur:
        cur.execute("SELECT id FROM skill WHERE id = %s", (skill_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Skill nao encontrada")

        cur.execute(
            "SELECT id FROM user_skill WHERE user_id = %s AND skill_id = %s AND type = %s",
            (user["id"], skill_id, type),
        )
        if cur.fetchone():
            raise HTTPException(400, "Skill ja adicionada")

        cur.execute(
            "INSERT INTO user_skill (user_id, skill_id, type) VALUES (%s, %s, %s)",
            (user["id"], skill_id, type),
        )
        db.commit()
    return {"message": "Skill adicionada"}


@router.delete("/me/{user_skill_id}")
def remove_skill(user_skill_id: int, user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "SELECT id FROM user_skill WHERE id = %s AND user_id = %s",
            (user_skill_id, user["id"]),
        )
        if not cur.fetchone():
            raise HTTPException(404, "Skill nao encontrada")

        cur.execute("DELETE FROM user_skill WHERE id = %s", (user_skill_id,))
        db.commit()
    return {"message": "Skill removida"}
