from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import hash_password, clear_auth_cookie, get_current_user
from app.core.validation import (
    is_valid_name, is_valid_email, is_valid_cpf,
    is_valid_phone, is_valid_birth_date, is_strong_password,
)

router = APIRouter()


@router.post("/users/me/update")
def update_me(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    cpf: str = Form(...),
    phone: str = Form(...),
    birth_date: str = Form(...),
    password: str = Form(""),
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    error = None
    if not is_valid_name(name):
        error = "Nome deve ter no minimo 5 letras"
    elif not is_valid_email(email):
        error = "E-mail invalido"
    elif not is_valid_cpf(cpf):
        error = "CPF invalido"
    elif not is_valid_phone(phone):
        error = "Celular invalido"
    elif not is_valid_birth_date(birth_date):
        error = "Data de nascimento invalida (idade minima 16 anos)"
    elif password and not is_strong_password(password):
        error = "Senha deve ter 8+ caracteres com maiuscula, minuscula, numero e caractere especial"

    if not error:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM user WHERE email = %s AND id != %s", (email, user["id"]))
            if cur.fetchone():
                error = "Email ja cadastrado"
            else:
                cur.execute("SELECT id FROM user WHERE cpf = %s AND id != %s", (cpf, user["id"]))
                if cur.fetchone():
                    error = "CPF ja cadastrado"

    if error:
        return RedirectResponse(f"/profile?error={error}", status_code=303)

    fields = ["name = %s", "email = %s", "cpf = %s", "phone = %s", "birth_date = %s"]
    params = [name, email, cpf, phone, birth_date]
    if password:
        fields.append("password = %s")
        params.append(hash_password(password))
    params.append(user["id"])

    with db.cursor() as cur:
        cur.execute(f"UPDATE user SET {', '.join(fields)} WHERE id = %s", params)
        db.commit()

    return RedirectResponse("/profile?ok=1", status_code=303)


@router.post("/users/me/delete")
def delete_me(request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    with db.cursor() as cur:
        cur.execute("DELETE FROM user WHERE id = %s", (user["id"],))
        db.commit()
    response = RedirectResponse("/login", status_code=303)
    clear_auth_cookie(response)
    return response
