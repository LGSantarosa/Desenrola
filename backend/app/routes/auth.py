import os
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import (
    hash_password, verify_password, create_token,
    set_auth_cookie, clear_auth_cookie,
)
from app.core.validation import (
    is_valid_name, is_valid_email, is_valid_cpf,
    is_valid_phone, is_valid_birth_date, is_strong_password,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()


@router.post("/auth/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    cpf: str = Form(...),
    phone: str = Form(...),
    birth_date: str = Form(...),
    db: Connection = Depends(get_db),
):
    form = {"name": name, "email": email, "cpf": cpf, "phone": phone, "birth_date": birth_date}

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
    elif not is_strong_password(password):
        error = "Senha deve ter 8+ caracteres com maiuscula, minuscula, numero e caractere especial"

    if not error:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM user WHERE email = %s", (email,))
            if cur.fetchone():
                error = "Email ja cadastrado"
            else:
                cur.execute("SELECT id FROM user WHERE cpf = %s", (cpf,))
                if cur.fetchone():
                    error = "CPF ja cadastrado"

    if error:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": error, "form": form},
            status_code=400,
        )

    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO user (name, email, password, cpf, phone, birth_date)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, email, hash_password(password), cpf, phone, birth_date),
        )
        db.commit()
        user_id = cur.lastrowid
        cur.execute("SELECT id, role FROM user WHERE id = %s", (user_id,))
        u = cur.fetchone()

    response = RedirectResponse("/onboarding", status_code=303)
    set_auth_cookie(response, create_token(u["id"], u["role"]))
    return response


@router.post("/auth/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Connection = Depends(get_db),
):
    with db.cursor() as cur:
        cur.execute("SELECT id, password, role FROM user WHERE email = %s", (email,))
        user = cur.fetchone()

    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Email ou senha incorretos", "form": {"email": email}},
            status_code=400,
        )

    response = RedirectResponse("/dashboard", status_code=303)
    set_auth_cookie(response, create_token(user["id"], user["role"]))
    return response


@router.post("/auth/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    clear_auth_cookie(response)
    return response
