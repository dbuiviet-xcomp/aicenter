# labs.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from core import templates, db
from bson import ObjectId

router = APIRouter()

LAB_TYPES = ["NLP", "Picture", "Video", "Audio"]

def redirect_login_with_next(request: Request):
    from urllib.parse import quote
    next_url = quote(str(request.url))
    return RedirectResponse(url=f"/login?next={next_url}", status_code=HTTP_303_SEE_OTHER)

def ensure_logged_in(request: Request):
    return "user" in request.session

def has_access_permission(current_user: dict) -> bool:
    if current_user is None:
        return False
    roles = current_user.get("roles") or []
    # Ví dụ: kiểm tra quyền 'Quản lý nhân sự' mới được dùng labs
    if "Quản lý thư viện" in roles:
        return True
    return False

@router.get("/labs", response_class=HTMLResponse)
async def labs_list(request: Request):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền truy cập trang này.",
            "user": current_user
        }, status_code=403)

    labs = list(db.labs.find({}).sort("order", 1))  # Sắp xếp theo order tăng dần

    return templates.TemplateResponse("labs.html", {
        "request": request,
        "labs": labs,
        "error": None,
        "msg": None,
        "user": current_user,
        "lab_types": LAB_TYPES,
        "active_tab": "labs"
    })

@router.get("/labs/create", response_class=HTMLResponse)
async def create_lab_form(request: Request):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền truy cập chức năng này."
        }, status_code=403)

    return templates.TemplateResponse("lab_form.html", {
        "request": request,
        "lab": None,
        "lab_types": LAB_TYPES,
        "user": current_user,
        "action": "Tạo",
        "error": None,
        "msg": None,
        "active_tab": "labs"
    })

@router.post("/labs/create", response_class=HTMLResponse)
async def create_lab(request: Request,
                     name: str = Form(...),
                     link: str = Form(...),
                     public: str = Form(...),
                     active: str = Form(...),
                     mota: str = Form(''),
                     code: str = Form(''),
                     lab_type: str = Form(...),
                     order: float = Form(0)):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền thực hiện thao tác này."
        }, status_code=403)

    db.labs.insert_one({
        "name": name,
        "link": link,
        "public": public,
        "active": active,
        "mota": mota,
        "code": code,
        "lab_type": lab_type,
        "order": order
    })

    return RedirectResponse(url="/labs", status_code=HTTP_303_SEE_OTHER)


@router.get("/labs/edit/{lab_id}", response_class=HTMLResponse)
async def edit_lab_page(request: Request, lab_id: str):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền truy cập chức năng này."
        }, status_code=403)

    lab = db.labs.find_one({"_id": ObjectId(lab_id)})
    if not lab:
        return RedirectResponse(url="/labs", status_code=HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("lab_form.html", {
        "request": request,
        "lab": lab,  # đổi tên biến thành lab cho phù hợp form
        "action": "Sửa",
        "user": current_user,
        "active_tab": "labs"
    })


@router.post("/labs/edit/{lab_id}", response_class=HTMLResponse)
async def edit_lab(request: Request,
                   lab_id: str,
                   name: str = Form(...),
                   link: str = Form(...),
                   public: str = Form(...),
                   active: str = Form(...),
                   lab_type: str = Form(...),
                   mota: str = Form(''),
                   code: str = Form(''),
                   order: float = Form(0)):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền thực hiện thao tác này."
        }, status_code=403)

    update_result = db.labs.update_one(
        {"_id": ObjectId(lab_id)},
        {"$set": {
            "name": name,
            "link": link,
            "public": public,
            "active": active,
            "lab_type": lab_type,
            "mota": mota,
            "code": code,
            "order": order
        }}
    )

    if update_result.matched_count == 0:
        error = "Lab không tồn tại."
        lab = {
            "_id": lab_id,
            "name": name,
            "link": link,
            "public": public,
            "active": active,
            "lab_type": lab_type,
            "mota": mota,
            "code": code,
            "order": order
        }
        return templates.TemplateResponse("lab_form.html", {
            "request": request,
            "lab": lab,
            "action": "Sửa",
            "user": current_user,
            "error": error,
            "active_tab": "labs"
        })

    return RedirectResponse("/labs", status_code=HTTP_303_SEE_OTHER)

@router.get("/labs/delete/{lab_id}")
async def delete_lab(lab_id: str, request: Request):
    if not ensure_logged_in(request):
        return redirect_login_with_next(request)

    current_user = request.session.get("user")
    if not has_access_permission(current_user):
        return templates.TemplateResponse("access_denied.html", {
            "request": request,
            "message": "Bạn không có quyền thực hiện thao tác này."
        }, status_code=403)

    db.labs.delete_one({"_id": ObjectId(lab_id)})
    return RedirectResponse("/labs", status_code=HTTP_303_SEE_OTHER)