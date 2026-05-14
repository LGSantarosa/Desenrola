import os
import uuid
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

router = APIRouter()


@router.post("/upload/avatar")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    redirect_to: str = Form("/onboarding"),
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    if not file.content_type or not file.content_type.startswith("image/"):
        return RedirectResponse(redirect_to + "?avatar=invalid", status_code=303)

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        return RedirectResponse(redirect_to + "?avatar=toolarge", status_code=303)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4()}.{ext}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(content)

    with db.cursor() as cur:
        cur.execute("UPDATE user SET avatar = %s WHERE id = %s", (filename, user["id"]))
        db.commit()

    return RedirectResponse(redirect_to, status_code=303)

# Rotas — upload de avatar

