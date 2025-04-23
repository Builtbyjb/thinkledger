from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, Response, JSONResponse
from datetime import datetime, timedelta, timezone
import os
from redis import Redis
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from utils.util import generate_crypto_string
from sqlmodel import Session
from database.postgres.postgres_db  import get_db
from database.redis.redis import get_redis
from database.postgres.postgres_schema import User
from typing import Optional


router = APIRouter(prefix="/auth/google/callback")

TOKEN_URL = "https://oauth2.googleapis.com/token"

def add_user_pg(db: Session, user_info) -> bool:
  """
    Save userinfo to postgres database
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
  except Exception as e:
    print(e)
    return False
  return True


def add_user_redis(redis: Redis,
  user_id: str,
  session_id: str,
  username: str,
  access_token: str,
  refresh_token: Optional[str] = None
) -> bool:
  """
    Save userinfo to redis database
  """
  try:
    redis.set(session_id, user_id, ex=3600 * 24 * 7) # set expire data to one week
    redis.set(f"username:{user_id}", username, ex=3600)
    redis.set(f"user_id:{user_id}", user_id) # For use later
    redis.set(f"username:{user_id}", username)
    redis.set(f"access_token:{user_id}", access_token)
    if refresh_token is not None:
      redis.set(f"refresh_token:{user_id}", refresh_token)
  except Exception as e:
    print(e)
    return False
  return True


@router.get("/sign-in")
async def google_sign_in_callback(
  request: Request,
  db: Session = Depends(get_db),
  redis: Redis = Depends(get_redis)
) -> Response:
  """
    Completes google sign-in oauth flow
  """
  # Verify state parameter
  if request.query_params.get("state") != request.cookies.get("state"):
    print("Invalid state parameter")
    return Response(status_code=400, content="Invalid state parameter")

  CLIENT_ID = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
  CLIENT_SECRET = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
  REDIRECT_URL = os.getenv("GOOGLE_SIGNIN_REDIRECT_URL")

  # Get authorization tokens
  try:
    code = request.query_params.get("code")
    payload = {
      "code": code,
      "client_id": CLIENT_ID,
      "client_secret": CLIENT_SECRET,
      "redirect_uri": REDIRECT_URL,
      "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=payload)
    token = response.json()
  except Exception as e:
    print("Failed to get authorization tokens")
    return Response(status_code=500, content=str(e))

  # Get user information
  try:
    user_info = id_token.verify_oauth2_token(
      token["id_token"],
      google_requests.Request(),
      CLIENT_ID
    )
  except Exception as e:
    print(e)
    return Response(status_code=400, content=str(e))

  # print(user_info)

  user_id = str(user_info.get("sub"))
  username = str(user_info.get("name"))
  access_token = str(token["access_token"])
  refresh_token = None

  try: refresh_token = token["refresh_token"]
  except KeyError: pass

  session_id: str = generate_crypto_string()

  # Check if the user exists before adding to database
  user = db.get(User, user_id)
  if user is None:
    is_added = add_user_pg(db, user_info)
    if not is_added:
      return Response(status_code=500, content="Internal server error")

  is_added = add_user_redis(redis, user_id, session_id, username, access_token, refresh_token)
  if not is_added:
    return Response(status_code=500, content="Internal server error")

  # result = redis.delete("username:123")

  # Set user authentication cookie
  response = RedirectResponse(url="/home", status_code=302)
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


@router.get("/services")
async def google_service_callback(request: Request, redis = Depends(get_redis)):
  """
    Completes getting google service tokens oauth flow
  """
  if request.cookies.get("state") != request.query_params.get("state"):
    return Response(status_code=400, content="Invalid state")

  CLIENT_ID = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
  CLIENT_SECRET = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
  REDIRECT_URL = os.getenv("GOOGLE_SERVICE_REDIRECT_URL")

  # Get authorization tokens
  try:
    code = request.query_params.get("code")
    payload = {
      "code": code,
      "client_id": CLIENT_ID,
      "client_secret": CLIENT_SECRET,
      "redirect_uri": REDIRECT_URL,
      "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=payload)
    token = response.json()
  except Exception as e:
    print("Failed to get authorization tokens")
    return Response(status_code=500, content=str(e))

  session_id = request.cookies.get("session_id")
  user_id = str(redis.get(session_id))
  if user_id is None: return JSONResponse(
    content={"error":"Unauthorized"},
    status_code=401
  )

  # print(token)
  access_token = token.get("access_token")
  refresh_token = token.get("refresh_token")

  try:
    redis.set(f"service_access_token:{user_id}", access_token)
    if refresh_token is not None:
      redis.set(f"service_refresh_token:{user_id}", refresh_token)
  except Exception as e:
    print(e)
    return JSONResponse(
      content={"error": "Internal Server Error"},
      status_code=500
    )

  print("tokens gotten")
  return RedirectResponse("/google", status_code=302)
