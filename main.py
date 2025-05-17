import os, multiprocessing, signal, sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from web.routes import google, legal, support, user_auth, integrations, plaid, join_waitlist, index
from dotenv import load_dotenv
from database.postgres.postgres_db import create_db_and_tables
from web.middleware.rate_limiter import RateLimiter
from fastapi.templating import Jinja2Templates
from core.core import core
from typing import Any
from contextlib import asynccontextmanager
from utils.logger import log
import asyncio


# Load .env file
load_dotenv()
exit_process = multiprocessing.Event()
core_process = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
  global core_process
  try:
    create_db_and_tables()
    exit_process.clear() # Ensure the exit process is cleared before starting a new core process
    core_process = multiprocessing.Process(target=core, args=(exit_process,), daemon=True)
    core_process.start()
    yield
  except asyncio.CancelledError: pass
  finally:
    if core_process: core_process.close()
    log.info("Shutting down gracefully...")


def signal_handler(sig:Any, frame:Any) -> None:
  log.info(f"Main process received signal {sig}, initiating shutdown...")
  exit_process.set()

  # Give the worker process some time to clean up
  if core_process:
    core_process.join(timeout=10)
    if core_process.is_alive():
      log.info("Core process did not exit in time, forcing termination!!")
      core_process.terminate()
  sys.exit(0)

# Register signal handlers, Handle KeyboardInterrupt
signal.signal(signal.SIGTERM, signal_handler)
# signal.signal(signal.SIGINT, signal_handler)


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
async def ping() -> JSONResponse:
  thread_alive = core_process.is_alive() if core_process else False
  env_check = "Good" if os.getenv("ENV_CHECK") else "Bad"
  return JSONResponse(
    content={
    "thread_running": thread_alive,
    "shutdown_signal_set": exit_process.is_set(),
    "env_check": env_check,
    "response": "pong"
  },
  status_code=200
  )


# Handles page not found
@app.exception_handler(404)
async def not_found(request: Request, exc: Exception) -> HTMLResponse:
  return templates.TemplateResponse(request=request, name="not_found.html")
