from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routes import (
    google_callback,
    legal,
    support,
    user_auth,
    integrations,
    plaid,
    google_service_token
)
from templates.content.features import FEATURES
from templates.content.benefits import BENEFITS
from utils.styles import BTN_STYLE_FULL, BTN_STYLE_OUTLINE, HOVER
from dotenv import load_dotenv
from database.postgres.postgres_db import create_db_and_tables

# Load .env file
load_dotenv()

# 	e.Use(middleware.Cors())
# 	e.Use(middleware.RequestTimer())
# 	e.Use(middleware.RateLimiter())
# 	e.Use(middleware.Recover())

# e.POST("/join-waitlist", h.JoinWaitlist)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(support.router)
app.include_router(legal.router)
app.include_router(user_auth.router)
app.include_router(google_callback.router)
app.include_router(integrations.router)
app.include_router(plaid.router)
app.include_router(google_service_token.router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    return {"ping": "pong"}


@app.get("/")
async def Index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="guest/index.html",
        context={
            "features": FEATURES,
            "benefits": BENEFITS,
            "btn_style_full": BTN_STYLE_FULL,
            "btn_style_outline": BTN_STYLE_OUTLINE
        }
    )


@app.get("/home")
async def Home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/home.html",
        context={
            "hover": HOVER
        }
    )


# Handles page not found
@app.exception_handler(404)
async def NotFound(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="not_found.html",
    )
