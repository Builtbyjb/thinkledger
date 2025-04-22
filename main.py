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
  google_service_token,
  join_waitlist,
)
from templates.content.features import FEATURES
from templates.content.benefits import BENEFITS
from utils.styles import BTN_STYLE_FULL, BTN_STYLE_OUTLINE, HOVER
from dotenv import load_dotenv
from database.postgres.postgres_db import create_db_and_tables
from middleware.rate_limiter import RateLimiter
from middleware.authentication import auth_required

# Load .env file
load_dotenv()

app = FastAPI()

@app.on_event("startup")
def on_startup():
  create_db_and_tables()

# Middleware
app.add_middleware(RateLimiter)

# Routes
app.include_router(support.router)
app.include_router(legal.router)
app.include_router(user_auth.router)
app.include_router(google_callback.router)
app.include_router(integrations.router)
app.include_router(plaid.router)
app.include_router(google_service_token.router)
app.include_router(join_waitlist.router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
  return {"ping": "pong"}


@app.get("/")
async def Index(request: Request):
  # TODO: Check if a user authenticated. if so redirect the user to /home
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
@auth_required(mode="strict")
async def Home(request: Request):
  username = request.state.username
  return templates.TemplateResponse(
    request=request,
    name="auth/home.html",
    context={
      "username": username,
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
