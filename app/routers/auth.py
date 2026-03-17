import os
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

ADMIN_ID = os.getenv("ADMIN_ID", "admin")
ADMIN_PW = os.getenv("ADMIN_PW", "admin")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if request.session.get("logged_in"):
        return RedirectResponse(url="/staff", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if request.session.get("logged_in"):
        return RedirectResponse(url="/staff", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_ID and password == ADMIN_PW:
        request.session["logged_in"] = True
        return RedirectResponse(url="/staff", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "IDまたはパスワードが正しくありません"})


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
