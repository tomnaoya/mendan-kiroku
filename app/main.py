import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from .database import engine
from . import models
from .routers import auth, staff, interviews

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="面談記録システム")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie="pulse_session")

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth.router)
app.include_router(staff.router)
app.include_router(interviews.router)
