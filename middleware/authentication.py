from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from typing import Literal, Callable
from functools import wraps
from redis import Redis
from database.redis.redis import gen_redis, get_redis
from utils.auth_utils import verify_access_token, refresh_access_token
import os


# Authentication mode options
AuthMode = Literal["strict", "lax"]

def auth_request(session_id: str, redis: Redis) -> bool:
  """
    Authenticates a user by verifying their access token and refreshing it if necessary.
  """
  try:
    user_id = str(redis.get(session_id))
    access_token  = str(redis.get(f"access_token:{user_id}"))
  except Exception as e:
    print(f"Error fetching user data or access token: {e}")
    return False

  # Verify access token
  if not verify_access_token(access_token):
    # If access token verification fails, try refreshing the token
    try: refresh_token = str(redis.get(f"refresh_token:{user_id}"))
    except Exception as e:
      print(f"Error fetching refresh token: {e}")
      return False

    if refresh_token is None: return False

    client_id = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")

    if client_id is None: return False
    if client_secret is None: return False

    new_access_token, is_refreshed = refresh_access_token(refresh_token, client_id, client_secret)
    if not is_refreshed or new_access_token is None: return False

    try: redis.set(f"access_token:{user_id}", new_access_token)
    except Exception as e:
      print(f"Error setting new access token: {e}")
      return False

  return True


def get_name(session_id: str, redis: Redis) -> str:
  try:
    user_id = str(redis.get(session_id))
    username = str(redis.get(f"username:{user_id}"))
  except Exception as e:
    print(f"Error fetching user name or user id: {e}")
    return "John Doe"
  return username


def auth_required(mode: AuthMode = "strict"):
  def decorator(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
      session_id = request.cookies.get("session_id")
      if session_id is None:
        if mode == "strict": return RedirectResponse("/")
      else:
        redis = gen_redis(get_redis)
        if redis is None: raise HTTPException(status_code=400, detail="Internal Server Error")
        if mode == "strict":
          is_auth = auth_request(session_id, redis)
          if not is_auth: return RedirectResponse("/")
        username = get_name(session_id, redis)
        request.state.username = username
      return await func(request, *args, **kwargs)
    return wrapper
  return decorator
