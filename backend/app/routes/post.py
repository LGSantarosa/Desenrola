import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.routes.user import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/")
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()
    result = []
    for p in posts:
        author = db.query(User).filter(User.id == p.user_id).first()
        result.append({
            "id": p.id,
            "content": p.content,
            "image": p.image,
            "created_at": str(p.created_at),
            "author": {
                "id": author.id,
                "name": author.name,
                "avatar": author.avatar,
            },
        })
    return result

@router.post("/")
async def create_post(
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_name = None
    if image and image.filename:
        if not image.content_type.startswith("image/"):
            raise HTTPException(400, "Arquivo deve ser uma imagem")

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ext = image.filename.split(".")[-1] if "." in image.filename else "png"
        image_name = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, image_name)

        file_content = await image.read()
        with open(filepath, "wb") as f:
            f.write(file_content)

    post = Post(user_id=user.id, content=content, image=image_name)
    db.add(post)
    db.commit()
    return {"message": "Post criado"}

@router.delete("/{post_id}")
def delete_post(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post nao encontrado")
    if post.user_id != user.id:
        raise HTTPException(403, "Sem permissao")
    db.delete(post)
    db.commit()
    return {"message": "Post deletado"}
