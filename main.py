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
from contextlib import asynccontextmanager

# Load .env file
load_dotenv()
exit_thread = threading.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  core_thread = threading.Thread(target=core,args=(exit_thread,), daemon=True)
  core_thread.start()
  yield
  exit_thread.set()
  print("Shutdown core thread...")


app = FastAPI(lifespan=lifespan)

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
  return templates.TemplateResponse(request=request, name="not_found.html")
