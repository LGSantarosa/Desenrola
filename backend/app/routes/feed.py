from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.skill import UserSkill, Skill, Category
from app.routes.user import get_current_user

router = APIRouter(prefix="/feed", tags=["feed"])

@router.get("/")
def get_feed(
    category_id: Optional[int] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    my_teaches = db.query(UserSkill).filter(UserSkill.user_id == user.id, UserSkill.type == "teaches").all()
    my_learns = db.query(UserSkill).filter(UserSkill.user_id == user.id, UserSkill.type == "learns").all()
    my_teach_ids = {us.skill_id for us in my_teaches}
    my_learn_ids = {us.skill_id for us in my_learns}

    all_user_skills = db.query(UserSkill).filter(UserSkill.user_id != user.id).all()

    user_ids = set()
    for us in all_user_skills:
        if category_id:
            skill = db.query(Skill).filter(Skill.id == us.skill_id).first()
            if skill.category_id != category_id:
                continue
        user_ids.add(us.user_id)

    results = []
    for uid in user_ids:
        other = db.query(User).filter(User.id == uid).first()
        teaches = db.query(UserSkill).filter(UserSkill.user_id == uid, UserSkill.type == "teaches").all()
        learns = db.query(UserSkill).filter(UserSkill.user_id == uid, UserSkill.type == "learns").all()

        teach_skills = []
        for us in teaches:
            skill = db.query(Skill).filter(Skill.id == us.skill_id).first()
            teach_skills.append({"id": skill.id, "name": skill.name})

        learn_skills = []
        for us in learns:
            skill = db.query(Skill).filter(Skill.id == us.skill_id).first()
            learn_skills.append({"id": skill.id, "name": skill.name})

        their_teach_ids = {us.skill_id for us in teaches}
        their_learn_ids = {us.skill_id for us in learns}

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
                "id": other.id,
                "name": other.name,
                "avatar": other.avatar,
            },
            "teaches": teach_skills,
            "learns": learn_skills,
            "score": score,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
