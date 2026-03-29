from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import hash_password, decode_token
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(401, "Usuario nao encontrado")
        return user
    except Exception:
        raise HTTPException(401, "Token invalido")

@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user

@router.put("/me", response_model=UserResponse)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        existing = db.query(User).filter(User.email == data.email, User.id != user.id).first()
        if existing:
            raise HTTPException(400, "Email ja cadastrado")
        user.email = data.email
    if data.password is not None:
        user.password = hash_password(data.password)
    if data.cpf is not None:
        existing = db.query(User).filter(User.cpf == data.cpf, User.id != user.id).first()
        if existing:
            raise HTTPException(400, "CPF ja cadastrado")
        user.cpf = data.cpf
    if data.phone is not None:
        user.phone = data.phone
    if data.birth_date is not None:
        user.birth_date = data.birth_date

    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    from app.models.skill import UserSkill, Skill
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario nao encontrado")

    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user.id).all()
    teaches = []
    learns = []
    for us in user_skills:
        skill = db.query(Skill).filter(Skill.id == us.skill_id).first()
        if us.type == "teaches":
            teaches.append(skill.name)
        else:
            learns.append(skill.name)

    return {
        "id": user.id,
        "name": user.name,
        "avatar": user.avatar,
        "role": user.role,
        "teaches": teaches,
        "learns": learns,
    }

@router.delete("/me")
def delete_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(user)
    db.commit()
    return {"message": "Conta deletada"}
