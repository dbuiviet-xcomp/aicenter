from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from core import db, templates
from passlib.context import CryptContext
from urllib.parse import unquote

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/login")
async def login_get(request: Request, next: str = "/"):
    # next: URL muốn redirect sau login, mặc định là /
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "next": next})

@router.post("/login")
async def login_post(request: Request,
                     phone: str = Form(...),
                     password: str = Form(...),
                     next: str = Form("/")):
    user = db.users.find_one({"phone": phone})

    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Số điện thoại không tồn tại", "next": next})

    if user.get("password") is None:
        hashed = pwd_context.hash(password)
        db.users.update_one({"phone": phone}, {"$set": {"password": hashed}})
    else:
        if not pwd_context.verify(password, user.get("password")):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Mật khẩu không đúng", "next": next})

    request.session['user'] = {
        "_id": str(user["_id"]),
        "name": user.get("username"),
        "phone": phone,
        "roles": user.get("roles", [])  # Lấy luôn roles vào session
    }

    print(request.session['user'])

    # Giải mã URL next nếu được mã hoá
    next_url = unquote(next)
    return RedirectResponse(url=next_url, status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)