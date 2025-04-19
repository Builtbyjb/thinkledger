import redis
import os
import sys
from typing import Generator, Any, Callable, Optional


REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL is None: sys.exit("REDIS_URL environment variable is not set")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
  try:
    yield redis_client
  finally:
    redis_client.close()


def gen_redis(get_redis: Callable[..., Generator[redis.Redis, Any, None]]) -> Optional[redis.Redis]:
  """
    Takens in a redis generator function any redis a Redis instance or None.
    The Depends function from fastapi does not handle generators well, if it not called
    within a route.
  """
  l = get_redis()
  for v in l:
    if isinstance(v, redis.Redis):
      return v
    else:
      continue
  return None
