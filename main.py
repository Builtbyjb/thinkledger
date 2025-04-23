from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from web.routes import (
  google,
  legal,
  support,
  user_auth,
  integrations,
  plaid,
  join_waitlist,
  index,
)
from dotenv import load_dotenv
from database.postgres.postgres_db import create_db_and_tables
from web.middleware.rate_limiter import RateLimiter
from fastapi.templating import Jinja2Templates
import threading
from core.core import core

# Load .env file
load_dotenv()

app = FastAPI()
exit_thread = threading.Event()

@app.on_event("startup")
def on_startup():
  create_db_and_tables()
  core_thread = threading.Thread(target=core,args=(exit_thread,), daemon=True)
  core_thread.start()


@app.on_event("shutdown")
def on_shutdown():
  # Shut down core thread gracefully
  exit_thread.set()
  print("Shutting down core thread")

# Middleware
app.add_middleware(RateLimiter)

# Routes
app.include_router(index.router)
app.include_router(support.router)
app.include_router(legal.router)
app.include_router(user_auth.router)
app.include_router(google.router)
app.include_router(integrations.router)
app.include_router(plaid.router)
app.include_router(join_waitlist.router)

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Handles page not found
@app.exception_handler(404)
async def NotFound(request: Request, exc: HTTPException):
  return templates.TemplateResponse(
    request=request,
    name="not_found.html",
  )
