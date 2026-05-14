import os
import uuid
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from typing import Optional
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

router = APIRouter()


@router.post("/posts/create")
async def create_post(
    request: Request,
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    content = content.strip()
    if not content:
        return RedirectResponse("/dashboard", status_code=303)

    image_name = None
    if image and image.filename:
        if image.content_type and image.content_type.startswith("image/"):
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            ext = image.filename.split(".")[-1] if "." in image.filename else "png"
            image_name = f"{uuid.uuid4()}.{ext}"
            file_content = await image.read()
            with open(os.path.join(UPLOAD_DIR, image_name), "wb") as f:
                f.write(file_content)

    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO post (user_id, content, image) VALUES (%s, %s, %s)",
            (user["id"], content, image_name),
        )
        db.commit()

    return RedirectResponse("/dashboard", status_code=303)


@router.post("/posts/{post_id}/delete")
def delete_post(post_id: int, request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    with db.cursor() as cur:
        cur.execute("SELECT user_id FROM post WHERE id = %s", (post_id,))
        post = cur.fetchone()
        if post and post["user_id"] == user["id"]:
            cur.execute("DELETE FROM post WHERE id = %s", (post_id,))
            db.commit()

    return RedirectResponse("/dashboard", status_code=303)

# Rotas — publicacoes do feed (criar, deletar)

