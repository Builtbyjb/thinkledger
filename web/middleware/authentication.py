from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from typing import Literal, Callable, Optional
from functools import wraps
from redis import Redis
from database.redis.redis import gen_redis
from utils.auth_utils import auth_session
from typing import Any


# Authentication mode options
AuthMode = Literal["strict", "lax"]


def get_name(session_id: str, redis: Redis) -> Optional[str]:
  try:
    user_id = redis.get(session_id)
    if user_id is None: return None
    assert isinstance(user_id, str), "User ID should be a string"
    username = redis.get(f"username:{user_id}")
  except Exception as e:
    print(f"Error fetching user name or user id: {e}")
    return None
  if username is None: return None
  assert isinstance(username, str), "Username should be a string"
  return username


def auth_required(mode: AuthMode = "strict") -> Any:
  def decorator(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
      session_id = request.cookies.get("session_id")
      if session_id is None:
        if mode == "strict": return RedirectResponse("/")
      else:
        redis = gen_redis()
        if redis is None: raise HTTPException(status_code=400, detail="Internal Server Error")
        if mode == "strict":
          is_auth = auth_session(session_id)
          if not is_auth: return RedirectResponse("/")
        username = get_name(session_id, redis)
        if username is None: username = "John Doe"
        request.state.username = username
      return await func(request, *args, **kwargs)
    return wrapper
  return decorator
