from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class SwapRequest(Base):
    __tablename__ = "swap_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    offered_skill_id = Column(Integer, ForeignKey("skill.id"), nullable=False)
    desired_skill_id = Column(Integer, ForeignKey("skill.id"), nullable=False)
    status = Column(Enum("pending", "accepted", "rejected"), default="pending")
    created_at = Column(DateTime, default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    offered_skill = relationship("Skill", foreign_keys=[offered_skill_id])
    desired_skill = relationship("Skill", foreign_keys=[desired_skill_id])
