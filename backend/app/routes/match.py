from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.skill import UserSkill, Skill
from app.models.user import User
from app.routes.user import get_current_user

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/")
def find_matches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    my_teaches = db.query(UserSkill).filter(UserSkill.user_id == user.id, UserSkill.type == "teaches").all()
    my_learns = db.query(UserSkill).filter(UserSkill.user_id == user.id, UserSkill.type == "learns").all()

    my_teach_ids = {us.skill_id for us in my_teaches}
    my_learn_ids = {us.skill_id for us in my_learns}

    if not my_teach_ids or not my_learn_ids:
        return []

    candidates = db.query(UserSkill).filter(
        UserSkill.user_id != user.id,
        UserSkill.type == "teaches",
        UserSkill.skill_id.in_(my_learn_ids),
    ).all()

    candidate_ids = {us.user_id for us in candidates}

    matches = []
    for cid in candidate_ids:
        their_teaches = db.query(UserSkill).filter(UserSkill.user_id == cid, UserSkill.type == "teaches").all()
        their_learns = db.query(UserSkill).filter(UserSkill.user_id == cid, UserSkill.type == "learns").all()

        their_teach_ids = {us.skill_id for us in their_teaches}
        their_learn_ids = {us.skill_id for us in their_learns}

        they_teach_i_want = my_learn_ids & their_teach_ids
        i_teach_they_want = my_teach_ids & their_learn_ids

        if they_teach_i_want and i_teach_they_want:
            candidate_user = db.query(User).filter(User.id == cid).first()

            def skill_names(ids):
                return [db.query(Skill).filter(Skill.id == sid).first().name for sid in ids]

            matches.append({
                "user": {
                    "id": candidate_user.id,
                    "name": candidate_user.name,
                    "avatar": candidate_user.avatar,
                },
                "they_teach": skill_names(they_teach_i_want),
                "they_want": skill_names(i_teach_they_want),
            })

    return matches
