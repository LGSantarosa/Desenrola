import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pymysql.connections import Connection
from app.core.database import get_db
from app.routes.user import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), user: dict = Depends(get_current_user), db: Connection = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Arquivo deve ser uma imagem")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    with db.cursor() as cur:
        cur.execute("UPDATE user SET avatar = %s WHERE id = %s", (filename, user["id"]))
        db.commit()

    return {"avatar": filename}
