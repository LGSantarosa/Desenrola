from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.skill import Category, Skill, UserSkill
from app.routes.user import get_current_user
from app.models.user import User

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).all()
    result = []
    for cat in cats:
        skills = db.query(Skill).filter(Skill.category_id == cat.id).all()
        result.append({
            "id": cat.id,
            "name": cat.name,
            "skills": [{"id": s.id, "name": s.name} for s in skills],
        })
    return result

@router.get("/me")
def my_skills(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user.id).all()
    teaches = []
    learns = []
    for us in user_skills:
        skill = db.query(Skill).filter(Skill.id == us.skill_id).first()
        item = {"id": us.id, "skill_id": skill.id, "name": skill.name}
        if us.type == "teaches":
            teaches.append(item)
        else:
            learns.append(item)
    return {"teaches": teaches, "learns": learns}

@router.post("/me")
def add_skill(skill_id: int, type: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if type not in ("teaches", "learns"):
        raise HTTPException(400, "Tipo deve ser 'teaches' ou 'learns'")

    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill nao encontrada")

    existing = db.query(UserSkill).filter(
        UserSkill.user_id == user.id,
        UserSkill.skill_id == skill_id,
        UserSkill.type == type,
    ).first()
    if existing:
        raise HTTPException(400, "Skill ja adicionada")

    us = UserSkill(user_id=user.id, skill_id=skill_id, type=type)
    db.add(us)
    db.commit()
    return {"message": "Skill adicionada"}

@router.delete("/me/{user_skill_id}")
def remove_skill(user_skill_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    us = db.query(UserSkill).filter(UserSkill.id == user_skill_id, UserSkill.user_id == user.id).first()
    if not us:
        raise HTTPException(404, "Skill nao encontrada")
    db.delete(us)
    db.commit()
    return {"message": "Skill removida"}
