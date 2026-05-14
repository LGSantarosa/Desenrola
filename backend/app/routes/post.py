import os
import uuid
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
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


@router.post("/posts/{post_id}/like")
def toggle_like(post_id: int, request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    with db.cursor() as cur:
        cur.execute("SELECT id FROM post WHERE id = %s", (post_id,))
        if not cur.fetchone():
            return RedirectResponse("/dashboard", status_code=303)

        cur.execute(
            "SELECT id FROM post_like WHERE post_id = %s AND user_id = %s",
            (post_id, user["id"]),
        )
        existing = cur.fetchone()
        if existing:
            cur.execute("DELETE FROM post_like WHERE id = %s", (existing["id"],))
        else:
            cur.execute(
                "INSERT INTO post_like (post_id, user_id) VALUES (%s, %s)",
                (post_id, user["id"]),
            )
        db.commit()

    return RedirectResponse(f"/dashboard#post-{post_id}", status_code=303)


@router.post("/comments/create")
def create_comment(
    request: Request,
    post_id: int = Form(...),
    content: str = Form(...),
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    content = content.strip()
    if not content:
        return RedirectResponse("/dashboard", status_code=303)

    new_id = None
    with db.cursor() as cur:
        cur.execute("SELECT id FROM post WHERE id = %s", (post_id,))
        if not cur.fetchone():
            return RedirectResponse("/dashboard", status_code=303)
        cur.execute(
            "INSERT INTO comment (post_id, user_id, content) VALUES (%s, %s, %s)",
            (post_id, user["id"], content),
        )
        new_id = cur.lastrowid
        db.commit()

    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse({"id": new_id})
    return RedirectResponse(f"/dashboard#post-{post_id}", status_code=303)


@router.post("/comments/{comment_id}/delete")
def delete_comment(comment_id: int, request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    post_id = None
    with db.cursor() as cur:
        cur.execute("SELECT user_id, post_id FROM comment WHERE id = %s", (comment_id,))
        c = cur.fetchone()
        if c and c["user_id"] == user["id"]:
            post_id = c["post_id"]
            cur.execute("DELETE FROM comment WHERE id = %s", (comment_id,))
            db.commit()

    target = f"/dashboard#post-{post_id}" if post_id else "/dashboard"
    return RedirectResponse(target, status_code=303)


