import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymysql.connections import Connection
from app.core.database import get_db
from app.core.auth import (
    get_current_user, COOKIE_NAME, decode_token, create_token, set_auth_cookie,
)
from app.routes import auth, user, skill, swap, upload, post

app = FastAPI(title="desenrola!")


@app.middleware("http")
async def refresh_session(request: Request, call_next):
    response = await call_next(request)
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            payload = decode_token(token)
            new_token = create_token(payload["user_id"], payload["role"])
            set_auth_cookie(response, new_token)
        except Exception:
            pass
    return response


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(skill.router)
app.include_router(swap.router)
app.include_router(upload.router)
app.include_router(post.router)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

uploads_dir = os.path.join(BASE_DIR, "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def fetch_categories(db):
    with db.cursor() as cur:
        cur.execute("SELECT id, name FROM category ORDER BY name")
        cats = cur.fetchall()
        result = []
        for c in cats:
            cur.execute("SELECT id, name FROM skill WHERE category_id = %s ORDER BY name", (c["id"],))
            result.append({"id": c["id"], "name": c["name"], "skills": cur.fetchall()})
    return result


def fetch_user_skills(db, user_id):
    with db.cursor() as cur:
        cur.execute(
            """SELECT us.type, s.id, s.name FROM user_skill us
               JOIN skill s ON s.id = us.skill_id
               WHERE us.user_id = %s""",
            (user_id,),
        )
        rows = cur.fetchall()
    teaches = [{"id": r["id"], "name": r["name"]} for r in rows if r["type"] == "teaches"]
    learns = [{"id": r["id"], "name": r["name"]} for r in rows if r["type"] == "learns"]
    return teaches, learns


def compute_match(my_teaches, my_learns, their_teaches, their_learns):
    my_teach_ids = {s["id"] for s in my_teaches}
    my_learn_ids = {s["id"] for s in my_learns}
    their_teach_ids = {s["id"] for s in their_teaches}
    their_learn_ids = {s["id"] for s in their_learns}

    they_teach_i_want = my_learn_ids & their_teach_ids
    i_teach_they_want = my_teach_ids & their_learn_ids

    if they_teach_i_want and i_teach_they_want:
        score = 3
    elif they_teach_i_want:
        score = 2
    elif i_teach_they_want:
        score = 1
    else:
        score = 0

    offered_id = next(iter(i_teach_they_want), None)
    desired_id = next(iter(they_teach_i_want), None)
    return score, offered_id, desired_id


def discover_people(db, user_id, category_id=None):
    my_teaches, my_learns = fetch_user_skills(db, user_id)

    with db.cursor() as cur:
        if category_id:
            cur.execute(
                """SELECT DISTINCT us.user_id FROM user_skill us
                   JOIN skill s ON s.id = us.skill_id
                   WHERE us.user_id != %s AND s.category_id = %s""",
                (user_id, category_id),
            )
        else:
            cur.execute("SELECT DISTINCT user_id FROM user_skill WHERE user_id != %s", (user_id,))
        user_ids = [r["user_id"] for r in cur.fetchall()]

    people = []
    for uid in user_ids:
        with db.cursor() as cur:
            cur.execute("SELECT id, name, avatar FROM user WHERE id = %s", (uid,))
            other = cur.fetchone()
            if not other:
                continue
        teaches, learns = fetch_user_skills(db, uid)
        score, offered_id, desired_id = compute_match(my_teaches, my_learns, teaches, learns)
        people.append({
            "user": other,
            "teaches": teaches,
            "learns": learns,
            "score": score,
            "offered_id": offered_id,
            "desired_id": desired_id,
        })

    people.sort(key=lambda x: x["score"], reverse=True)
    return people


def format_swap(db, s):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, avatar, email, phone FROM user WHERE id = %s", (s["sender_id"],))
        sender = cur.fetchone()
        cur.execute("SELECT id, name, avatar, email, phone FROM user WHERE id = %s", (s["receiver_id"],))
        receiver = cur.fetchone()
        cur.execute("SELECT name FROM skill WHERE id = %s", (s["offered_skill_id"],))
        offered = cur.fetchone()
        cur.execute("SELECT name FROM skill WHERE id = %s", (s["desired_skill_id"],))
        desired = cur.fetchone()

    item = {
        "id": s["id"],
        "status": s["status"],
        "created_at": s["created_at"],
        "sender": sender,
        "receiver": receiver,
        "offered_skill": offered["name"] if offered else "",
        "desired_skill": desired["name"] if desired else "",
    }
    if s["status"] != "accepted":
        item["sender"] = {k: v for k, v in sender.items() if k not in ("email", "phone")}
        item["receiver"] = {k: v for k, v in receiver.items() if k not in ("email", "phone")}
    return item


def redirect_login():
    return RedirectResponse("/login", status_code=303)


@app.get("/")
def page_index(request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login")
def page_login(request: Request, db: Connection = Depends(get_db)):
    if get_current_user(request, db):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "form": {}, "error": None})


@app.get("/register")
def page_register(request: Request, db: Connection = Depends(get_db)):
    if get_current_user(request, db):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request, "form": {}, "error": None})


@app.get("/dashboard")
def page_dashboard(request: Request, category_id: int = None, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return redirect_login()

    with db.cursor() as cur:
        cur.execute(
            """SELECT p.id, p.content, p.image, p.created_at,
                      u.id AS author_id, u.name AS author_name, u.avatar AS author_avatar
               FROM post p JOIN user u ON u.id = p.user_id
               ORDER BY p.created_at DESC LIMIT 50"""
        )
        posts = cur.fetchall()

    categories = fetch_categories(db)
    people = discover_people(db, user["id"], category_id)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "posts": posts,
        "categories": categories,
        "people": people,
        "active_category": category_id,
    })


@app.get("/onboarding")
def page_onboarding(request: Request, ok: int = None, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return redirect_login()
    categories = fetch_categories(db)
    # acha o que o usuario ja tem cadastrado pra  os checkboxes
    teaches, learns = fetch_user_skills(db, user["id"])
    selected_teach_ids = [s["id"] for s in teaches]
    selected_learn_ids = [s["id"] for s in learns]
    # se ja tem alguma skill ta editando
    is_editing = bool(selected_teach_ids or selected_learn_ids)
    return templates.TemplateResponse("onboarding.html", {
        "request": request,
        "user": user,
        "categories": categories,
        "selected_teach_ids": selected_teach_ids,
        "selected_learn_ids": selected_learn_ids,
        "is_editing": is_editing,
        "ok": ok,
    })


@app.get("/match")
def page_match(request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return redirect_login()
    people = discover_people(db, user["id"])
    my_teaches, _ = fetch_user_skills(db, user["id"])
    return templates.TemplateResponse("match.html", {
        "request": request,
        "user": user,
        "people": people,
        "my_teaches": my_teaches,
    })


@app.get("/profile")
def page_profile(
    request: Request,
    ok: int = None,
    error: str = None,
    db: Connection = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return redirect_login()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "birth_date": user["birth_date"].isoformat() if user["birth_date"] else "",
        "ok": ok,
        "error": error,
    })


@app.get("/swaps")
def page_swaps(request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return redirect_login()

    with db.cursor() as cur:
        cur.execute("SELECT * FROM swap_request WHERE receiver_id = %s ORDER BY created_at DESC", (user["id"],))
        received_raw = cur.fetchall()
        cur.execute("SELECT * FROM swap_request WHERE sender_id = %s ORDER BY created_at DESC", (user["id"],))
        sent_raw = cur.fetchall()

    received = [format_swap(db, s) for s in received_raw]
    sent = [format_swap(db, s) for s in sent_raw]

    return templates.TemplateResponse("swaps.html", {
        "request": request,
        "user": user,
        "received": received,
        "sent": sent,
    })


@app.get("/user/{user_id}")
def page_user(user_id: int, request: Request, db: Connection = Depends(get_db)):
    me = get_current_user(request, db)
    if not me:
        return redirect_login()

    with db.cursor() as cur:
        cur.execute("SELECT id, name, avatar FROM user WHERE id = %s", (user_id,))
        other = cur.fetchone()

    if not other:
        return templates.TemplateResponse("user.html", {
            "request": request,
            "user": me,
            "other": None,
        }, status_code=404)

    teaches, learns = fetch_user_skills(db, user_id)
    my_teaches, my_learns = fetch_user_skills(db, me["id"])
    score, offered_id, desired_id = compute_match(my_teaches, my_learns, teaches, learns)

    return templates.TemplateResponse("user.html", {
        "request": request,
        "user": me,
        "other": other,
        "teaches": teaches,
        "learns": learns,
        "offered_id": offered_id,
        "desired_id": desired_id,
        "is_self": other["id"] == me["id"],
    })

# Rotas — paginas (GET) que renderizam HTML via Jinja2

