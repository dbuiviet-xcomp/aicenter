from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from core import templates,db

# CORS
from fastapi.middleware.cors import CORSMiddleware

from routers.users import router as users_router
from routers.login import router as login_router
from routers.labs import router as labs_router
from api.nlp_api import router as nlp_api_router
from api.tts_api import router as tts_api_router

app = FastAPI()


# Middleware session để lưu trạng thái đăng nhập và ngôn ngữ
app.add_middleware(SessionMiddleware, secret_key="your-very-secret-random-string-32-chars")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://oa.zalo.me",
        "http://localhost:3000",
        "https://miniapp.zaloplatforms.com",
        "https://center.ai.vn",
        "https://h5.zdn.vn" # thêm domain Zalo gọi API
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Mount static file thư mục
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users_router)
app.include_router(login_router)
app.include_router(labs_router)

app.include_router(nlp_api_router)

app.include_router(tts_api_router)

SUPPORTED_LANGUAGES = ["vi", "en", "fr", "ru", "cn", "jp", "kr", "lao", "cam"]
DEFAULT_LANGUAGE = "vi"


def get_language(request: Request):
    # Thứ tự lấy ngôn ngữ: session -> query param -> mặc định
    lang = request.session.get("lang")
    if not lang:
        lang = request.query_params.get("lang")
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    return lang


@app.get("/set-lang/{lang_code}")
def set_language(lang_code: str, request: Request):
    if lang_code not in SUPPORTED_LANGUAGES:
        lang_code = DEFAULT_LANGUAGE
    # lưu vào session
    request.session["lang"] = lang_code

    # Redirect về trang trước đó, fallback về home
    referrer = request.headers.get("referer") or "/"
    response = RedirectResponse(url=referrer)
    return response

# app_main.py (hoặc module nào khác)
# from core import run_mistral_instruct

# Ví dụ gọi thực tế
# resp = run_mistral_instruct("[INST] Summarize the effects of aspirin. [/INST]")
# print(resp)

@app.get("/", response_class=HTMLResponse)
def home_intro(request: Request):
    user = request.session.get("user")
    lang = get_language(request)
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")


    return templates.TemplateResponse("home_main.html", {
        "request": request,
        "active_tab": "home",
        "host":host,
        "user": user,
        "lang": lang

    })

@app.get("/nlp", response_class=HTMLResponse)
async def labs_list(request: Request):
    labs = list(db.labs.find({"lab_type": "NLP","public": "public", "active": "active"}).sort("order", 1))

    return templates.TemplateResponse("nlp.html", {
        "request": request,
        "labs": labs,
        "error": None,
        "msg": None,

        "active_tab": "labs"
    })


# Để các route còn lại cũng có ngôn ngữ bạn cần bổ sung tương tự (ví dụ trong routers)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)