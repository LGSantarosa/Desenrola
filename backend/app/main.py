import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import auth, user, skill, match, swap, upload, feed, post

app = FastAPI(title="desenrola! API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(skill.router)
app.include_router(match.router)
app.include_router(swap.router)
app.include_router(upload.router)
app.include_router(feed.router)
app.include_router(post.router)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

uploads_dir = os.path.join(BASE_DIR, "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
def page_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def page_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard")
def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/onboarding")
def page_onboarding(request: Request):
    return templates.TemplateResponse("onboarding.html", {"request": request})


@app.get("/match")
def page_match(request: Request):
    return templates.TemplateResponse("match.html", {"request": request})


@app.get("/profile")
def page_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/swaps")
def page_swaps(request: Request):
    return templates.TemplateResponse("swaps.html", {"request": request})


@app.get("/user")
def page_user(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})
