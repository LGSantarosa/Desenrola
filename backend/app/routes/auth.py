from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_token
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email ja cadastrado")

    if db.query(User).filter(User.cpf == data.cpf).first():
        raise HTTPException(400, "CPF ja cadastrado")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        cpf=data.cpf,
        phone=data.phone,
        birth_date=data.birth_date,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.role)
    return {"token": token, "user": {"id": user.id, "name": user.name, "role": user.role}}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Email ou senha incorretos")

    token = create_token(user.id, user.role)
    return {"token": token, "user": {"id": user.id, "name": user.name, "role": user.role}}
