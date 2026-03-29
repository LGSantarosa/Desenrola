from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.swap import SwapRequest
from app.models.user import User
from app.models.skill import Skill
from app.routes.user import get_current_user

router = APIRouter(prefix="/swaps", tags=["swaps"])

@router.post("/")
def create_swap(receiver_id: int, offered_skill_id: int, desired_skill_id: int,
                user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if receiver_id == user.id:
        raise HTTPException(400, "Nao pode enviar troca pra voce mesmo")

    receiver = db.query(User).filter(User.id == receiver_id).first()
    if not receiver:
        raise HTTPException(404, "Usuario nao encontrado")

    existing = db.query(SwapRequest).filter(
        SwapRequest.sender_id == user.id,
        SwapRequest.receiver_id == receiver_id,
        SwapRequest.status == "pending",
    ).first()
    if existing:
        raise HTTPException(400, "Ja existe uma solicitacao pendente")

    swap = SwapRequest(
        sender_id=user.id,
        receiver_id=receiver_id,
        offered_skill_id=offered_skill_id,
        desired_skill_id=desired_skill_id,
    )
    db.add(swap)
    db.commit()
    return {"message": "Solicitacao enviada"}

@router.get("/received")
def received_swaps(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    swaps = db.query(SwapRequest).filter(SwapRequest.receiver_id == user.id).all()
    return [format_swap(s, db) for s in swaps]

@router.get("/sent")
def sent_swaps(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    swaps = db.query(SwapRequest).filter(SwapRequest.sender_id == user.id).all()
    return [format_swap(s, db) for s in swaps]

@router.put("/{swap_id}")
def update_swap(swap_id: int, status: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if status not in ("accepted", "rejected"):
        raise HTTPException(400, "Status deve ser 'accepted' ou 'rejected'")

    swap = db.query(SwapRequest).filter(SwapRequest.id == swap_id, SwapRequest.receiver_id == user.id).first()
    if not swap:
        raise HTTPException(404, "Solicitacao nao encontrada")

    if swap.status != "pending":
        raise HTTPException(400, "Solicitacao ja foi respondida")

    swap.status = status
    db.commit()
    return {"message": "Solicitacao " + ("aceita" if status == "accepted" else "recusada")}

def format_swap(s, db):
    sender = db.query(User).filter(User.id == s.sender_id).first()
    receiver = db.query(User).filter(User.id == s.receiver_id).first()
    offered = db.query(Skill).filter(Skill.id == s.offered_skill_id).first()
    desired = db.query(Skill).filter(Skill.id == s.desired_skill_id).first()
    result = {
        "id": s.id,
        "status": s.status,
        "created_at": str(s.created_at),
        "sender": {"id": sender.id, "name": sender.name, "avatar": sender.avatar},
        "receiver": {"id": receiver.id, "name": receiver.name, "avatar": receiver.avatar},
        "offered_skill": offered.name,
        "desired_skill": desired.name,
    }
    if s.status == "accepted":
        result["sender"]["email"] = sender.email
        result["sender"]["phone"] = sender.phone
        result["receiver"]["email"] = receiver.email
        result["receiver"]["phone"] = receiver.phone
    return result
