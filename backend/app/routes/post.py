import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pymysql.connections import Connection
from typing import Optional
from app.core.database import get_db
from app.routes.user import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/")
def list_posts(db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            """SELECT p.id, p.content, p.image, p.created_at,
                      u.id AS author_id, u.name AS author_name, u.avatar AS author_avatar
               FROM post p JOIN user u ON u.id = p.user_id
               ORDER BY p.created_at DESC LIMIT 50"""
        )
        posts = cur.fetchall()

    return [
        {
            "id": p["id"],
            "content": p["content"],
            "image": p["image"],
            "created_at": str(p["created_at"]),
            "author": {
                "id": p["author_id"],
                "name": p["author_name"],
                "avatar": p["author_avatar"],
            },
        }
        for p in posts
    ]


@router.post("/")
async def create_post(
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
    db: Connection = Depends(get_db),
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

    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO post (user_id, content, image) VALUES (%s, %s, %s)",
            (user["id"], content, image_name),
        )
        db.commit()
    return {"message": "Post criado"}


@router.delete("/{post_id}")
def delete_post(post_id: int, user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, user_id FROM post WHERE id = %s", (post_id,))
        post = cur.fetchone()
        if not post:
            raise HTTPException(404, "Post nao encontrado")
        if post["user_id"] != user["id"]:
            raise HTTPException(403, "Sem permissao")

        cur.execute("DELETE FROM post WHERE id = %s", (post_id,))
        db.commit()
    return {"message": "Post deletado"}
