from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from web.routes import google, legal, support, user_auth, integrations, plaid, join_waitlist, index
from dotenv import load_dotenv
from database.postgres.postgres_db import create_db_and_tables
from web.middleware.rate_limiter import RateLimiter
from fastapi.templating import Jinja2Templates
import threading
from core.core import core
from contextlib import asynccontextmanager
from utils.logger import log

# Load .env file
load_dotenv()
exit_thread = threading.Event()
core_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
  global core_thread
  create_db_and_tables()
  exit_thread.clear() # Ensure the exit thread is cleared before starting the core thread
  core_thread = threading.Thread(target=core, args=(exit_thread,), daemon=True)
  core_thread.start()
  yield
  exit_thread.set()
  core_thread.join()
  log.info("Shutdown core thread...")

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

# Health check
@app.get("/ping")
async def ping():
  thread_alive = core_thread.is_alive() if core_thread else False
  return {
    "thread_running": thread_alive,
    "shutdown_signal_set": exit_thread.is_set(),
    "response": "pong"
  }

# Handles page not found
@app.exception_handler(404)
async def NotFound(request: Request, exc: HTTPException):
  return templates.TemplateResponse(request=request, name="not_found.html")
