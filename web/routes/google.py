from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta, timezone
import os
from redis import Redis
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from utils.util import generate_crypto_string
from sqlmodel import Session
from database.postgres.postgres_db import get_db
from database.redis.redis import get_redis
from database.postgres.postgres_schema import User
from typing import Optional, Union
from enum import Enum
from utils.auth_utils import service_auth_config
from utils.constants import TOKEN_URL
from utils.logger import log
from fastapi import BackgroundTasks


router = APIRouter(prefix="/google", tags=["Google"])


def add_user_pg(db: Session, user_info) -> None:
  """
    Save user info to postgres database
  """
  new_user = User(
    id=user_info.get("sub"),
    email=user_info.get("email"),
    name=user_info.get("name"),
    given_name=user_info.get("given_name"),
    family_name=user_info.get("family_name"),
    picture=user_info.get("picture"),
  )
  try:
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log.info("User added to postgres database")
  except Exception as e:
    log.error(f"Error adding user to postgres database: {e}")


def add_user_redis(
  redis: Redis,
  user_id: str,
  session_id: str,
  username: str,
  access_token: str,
  refresh_token: Optional[str] = None
) -> None:
  """
    Save user info to redis database
  """
  # result = redis.delete("username:123")
  try:
    redis.set(session_id, user_id, ex=3600 * 24 * 7) # set expire data to one week
    redis.set(f"user_id:{user_id}", user_id) # For use later
    redis.set(f"username:{user_id}", username)
    redis.set(f"access_token:{user_id}", access_token)
    if refresh_token is not None: redis.set(f"refresh_token:{user_id}", refresh_token)
    log.info("User added to redis")
  except Exception as e:
    log.error(f"Error adding user to redis: {e}")


@router.get("/callback/sign-in", response_model=None)
async def google_sign_in_callback(
  request: Request,
  bg: BackgroundTasks,
  db: Session = Depends(get_db),
  redis: Redis = Depends(get_redis)
) -> Union[JSONResponse, RedirectResponse]:
  """
    Completes google sign-in oauth flow
  """
  # Verify state parameter
  if request.query_params.get("state") != request.cookies.get("state"):
    log.error("Invalid state parameter")
    return JSONResponse(content={"error":"Invalid state parameter"}, status_code=400)

  client_id = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
  client_secret = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
  server_url = os.getenv("SERVER_URL")

  assert client_id is not None, "Client ID is not set"
  assert client_secret is not None, "Client Secret is not set"
  assert server_url is not None, "Server URL is not set"

  redirect_url = f"{server_url}/google/callback/sign-in"

  # Get authorization tokens
  try:
    code = request.query_params.get("code")
    payload = {
      "code": code,
      "client_id": client_id,
      "client_secret": client_secret,
      "redirect_uri": redirect_url,
      "grant_type": "authorization_code"
    }
    res = requests.post(TOKEN_URL, data=payload)
    token = res.json()
  except Exception as e:
    log.error("Failed to get authorization tokens")
    return JSONResponse(content=str(e), status_code=500)

  # Get user information
  try:
    user_info = id_token.verify_oauth2_token(
      token["id_token"],
      google_requests.Request(),
      client_id
    )
  except Exception as e:
    log.error(e)
    return JSONResponse(content=str(e), status_code=500)

  # print(user_info)

  user_id = user_info.get("sub")
  username = user_info.get("name")
  access_token = token["access_token"]
  session_id: str = generate_crypto_string()
  refresh_token: Optional[str] = None
  try: refresh_token = token["refresh_token"]
  except KeyError: log.info("Refresh token not found")

  # Check if the user exists before adding to database
  user = db.get(User, user_id)
  if user is None:
    # Add user to database
    bg.add_task(add_user_pg, db, user_info)

  # Add user to redis
  bg.add_task(add_user_redis, redis, user_id, session_id, username, access_token, refresh_token)

  # Set user authentication cookie
  response: RedirectResponse = RedirectResponse(url="/home", status_code=302)
  expires = datetime.now(timezone.utc) + timedelta(days=7)
  response.set_cookie(
    key="session_id",
    value=session_id,
    expires=expires,
    path="/",
    secure=True,
    httponly=True,
    samesite="lax"
  )
  return response


@router.get("/callback/services", response_model=None)
async def google_service_callback(
  request: Request, redis = Depends(get_redis)
  ) -> Union[JSONResponse, RedirectResponse]:
  """
    Completes getting google service tokens oauth flow
  """
  if request.cookies.get("state") != request.query_params.get("state"):
    return JSONResponse(content={"error":"Invalid state parameter"}, status_code=400)

  client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
  client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
  server_url = os.getenv("SERVER_URL")

  assert client_id is not None, "Client ID is not set"
  assert client_secret is not None, "Client Secret is not set"
  assert server_url is not None, "Server URL is not set"

  redirect_url = f"{server_url}/google/callback/services"

  # Get authorization tokens
  try:
    code = request.query_params.get("code")
    payload = {
      "code": code,
      "client_id": client_id,
      "client_secret": client_secret,
      "redirect_uri": redirect_url,
      "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=payload)
    token = response.json()
  except Exception as e:
    log.error("Failed to get authorization tokens")
    return JSONResponse(content=str(e), status_code=500)

  session_id: Optional[str] = request.cookies.get("session_id")
  if session_id is None:
    log.error("Session ID not found")
    return RedirectResponse(url="/", status_code=302)

  user_id: Optional[str] = redis.get(session_id)
  if user_id is None:
    log.error("User not found")
    return JSONResponse(content={"error":"Unauthorized"}, status_code=401)

  # print(token)
  access_token: str = token.get("access_token")
  assert isinstance(access_token, str), "Access token is not a string"

  refresh_token: Optional[str] = token.get("refresh_token")

  try:
    redis.set(f"service_access_token:{user_id}", access_token)
    if refresh_token is not None: redis.set(f"service_refresh_token:{user_id}", refresh_token)
  except Exception as e:
    log.error(e)
    return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

  log.info("tokens gotten")
  return RedirectResponse("/google", status_code=302)


class GoogleScopes(Enum):
  sheets = "https://www.googleapis.com/auth/spreadsheets"
  drive = "https://www.googleapis.com/auth/drive.file"


@router.get("/services")
async def google_service_token(request: Request) -> JSONResponse:
  """
    Starts google service tokens oauth flow
  """
  scopes: list[str] = []

  google_sheet = request.query_params.get("google_sheet")
  google_drive = request.query_params.get("google_drive")

  if google_sheet == "true": scopes.append(GoogleScopes.sheets.value)
  if google_drive == "true": scopes.append(GoogleScopes.drive.value)

  if len(scopes) == 0: return JSONResponse(content={"error":"No scopes provided"}, status_code=400)

  # Get oauth service config
  config = service_auth_config(scopes)
  url, state = config.authorization_url(
     #  access_type="offline",
     # include_granted_scopes="true",
     # prompt="consent"
  )

  response = JSONResponse(content={"url": url}, status_code=200)
  expires = datetime.now(timezone.utc) + timedelta(minutes=5)
  response.set_cookie(
      key="state",
      value=state,
      expires=expires,
      path="/",
      secure=True,
      httponly=True,
      samesite="lax"
  )
  return response
