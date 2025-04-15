import redis
import os
import sys

REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL is None:
    sys.exit("REDIS_URL environment variable is not set")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis_client():
    yield redis_client
