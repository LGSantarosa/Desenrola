from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    cpf: str
    phone: str
    birth_date: date

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    phone: str
    birth_date: date
    role: str
    avatar: Optional[str]

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str
