from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    skills = relationship("Skill", back_populates="category")

class Skill(Base):
    __tablename__ = "skill"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="skills")

class UserSkill(Base):
    __tablename__ = "user_skill"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skill.id"), nullable=False)
    type = Column(Enum("teaches", "learns"), nullable=False)
    skill = relationship("Skill")
