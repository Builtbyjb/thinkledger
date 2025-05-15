from celery import Celery
import os
import sys


REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL is None: sys.exit("REDIS_URL environment variable is not set")

c = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)