from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from web.routes import google, legal, support, user_auth, integrations, plaid, join_waitlist, index
from dotenv import load_dotenv
from database.postgres.postgres_db import create_db_and_tables
from web.middleware.rate_limiter import RateLimiter
from fastapi.templating import Jinja2Templates
import threading
from core.core import core
from typing import Any
from contextlib import asynccontextmanager
from utils.logger import log
import asyncio

# Load .env file
load_dotenv()
exit_thread = threading.Event()
core_thread = None

def run_core(exit_thread: Any) -> None:
  """
  Run the core function in a separate thread.
  """
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  try: loop.run_until_complete(core(exit_thread))
  except Exception as e: log.error(f"Error in core thread: {e}")
  finally: loop.close()

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
  global core_thread
  create_db_and_tables()
  exit_thread.clear() # Ensure the exit thread is cleared before starting the core thread
  core_thread = threading.Thread(target=run_core, args=(exit_thread,), daemon=True)
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
async def ping() -> JSONResponse:
  thread_alive = core_thread.is_alive() if core_thread else False
  return JSONResponse(
    content={
    "thread_running": thread_alive,
    "shutdown_signal_set": exit_thread.is_set(),
    "response": "pong"
  },
  status_code=200
  )


# Handles page not found
@app.exception_handler(404)
async def not_found(request: Request) -> HTMLResponse:
  return templates.TemplateResponse(request=request, name="not_found.html")
