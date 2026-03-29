from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True)
    phone = Column(String(15), nullable=False)
    birth_date = Column(Date, nullable=False)
    role = Column(Enum("admin", "user"), default="user")
    avatar = Column(String(255), default=None)
    created_at = Column(DateTime, default=func.now())
