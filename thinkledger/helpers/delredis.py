#!/usr/bin/env python3

#############################################################################################
# WARNING: This script clears all the keys and values in a redis database. Use carefully!!! #
#############################################################################################

import os, sys
from dotenv import load_dotenv
import redis


def delete() -> None:
  redis_url = os.getenv("REDIS_URL")
  if redis_url is None: sys.exit("REDIS_URL environment variable is not set")
  redis_client = redis.Redis.from_url(redis_url)
  redis_client.flushall()
  print("Redis database cleared successfully")
  return None


if __name__ == "__main__":
  load_dotenv()
  delete()
