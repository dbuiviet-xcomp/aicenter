from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from core import templates, db
from urllib.parse import quote

router = APIRouter()

ROLE_NAMES = [
    "Quản lý nhân sự",
    "Quản lý thư viện"

]

def redirect_login_with_next(request: Request):
    next_url = quote(str(request.url))
    return RedirectResponse(url=f"/login?next={next_url}", status_code=HTTP_303_SEE_OTHER)

def ensure_logged_in(request: Request):
    return "user" in request.session

def has_access_permission(current_user: dict) -> bool:

    if current_user is None:
        return False
    # Kiểm tra số điện thoại đặc biệt
    if current_user.get("phone") == "0982571428":
        return True
    roles = current_user.get("roles") or []
    # Kiểm tra quyền "Quản lý nhân sự"
    if "Quản lý nhân sự" in roles:
        return True
    return False

@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền truy cập trang này.",
            "user": current_user
        }, status_code=403)

    users = list(db.users.find({}, {"_id": 0, "username": 1, "phone": 1, "roles": 1}))

    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "error": None,
        "msg": None,
        "user": current_user,
        "role_names": ROLE_NAMES,
    })

@router.get("/users/edit/{username}", response_class=HTMLResponse)
async def edit_user_page(request: Request, username: str):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền truy cập chức năng này."
        }, status_code=403)

    user = db.users.find_one({"username": username}, {"_id": 0})

    if not user:
        return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)

    user_roles = user.get("roles") or []

    return templates.TemplateResponse("edit_user.html", {
        "request": request,
        "user_to_edit": user,
        "roles": user_roles,
        "role_names": ROLE_NAMES,
        "user": current_user,
        "error": None,
        "msg": None
    })

@router.post("/users/edit/{username}", response_class=HTMLResponse)
async def edit_user(request: Request,
                    username: str,
                    phone: str = Form(...),
                    roles: list[str] = Form([]),
                    key: str = Form(...)):  # thêm trường key
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền thực hiện thao tác này."
        }, status_code=403)

    update_result = db.users.update_one(
        {"username": username},
        {"$set": {
            "phone": phone,
            "roles": roles,
            "key": key         # cập nhật trường key
        }}
    )

    if update_result.matched_count == 0:
        error = "Người dùng không tồn tại."
        user = {"username": username, "phone": phone, "roles": roles, "key": key}
        return templates.TemplateResponse("edit_user.html", {
            "request": request,
            "user_to_edit": user,
            "roles": roles,
            "role_names": ROLE_NAMES,
            "current_user": current_user,
            "error": error,
            "msg": None
        })

    return RedirectResponse("/users", status_code=HTTP_303_SEE_OTHER)

@router.post("/users/create")
async def create_user(request: Request,
                      username: str = Form(...),
                      phone: str = Form(...)):
    if not ensure_logged_in(request):
        return RedirectResponse(url="/login", status_code=303)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền thực hiện thao tác này."
        }, status_code=403)

    error = None
    existing_user = db.users.find_one({"username": username})

    if existing_user:
        error = "Người dùng này đã tồn tại."
    else:
        db.users.insert_one({
            "username": username,
            "phone": phone,
            "password": None,
            "roles": []
        })

    users = list(db.users.find({}, {"_id": 0, "username": 1, "phone": 1, "roles": 1}))
    current_user = request.session.get("user")

    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "error": error,
        "msg": None if error else "Tạo người dùng thành công!",
        "user": current_user,
        "role_names": ROLE_NAMES,
    })