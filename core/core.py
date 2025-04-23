from database.postgres.postgres_db import gen_db
from database.redis.redis import gen_redis
from database.postgres.postgres_schema import User
from sqlmodel import select
import time
from utils.core_utils import TaskPriority, Tasks
from core.celery import get_transaction

def core(exit_thread):
  print("Print starting core thread...")
  db = gen_db()
  if db is None: return

  redis = gen_redis()
  if redis is None: return

  while not exit_thread.is_set():
    time.sleep(60)
    users = db.exec(select(User)).all()
    for u in users:
      # TODO: Get user tasks
      # Check for tasks of High level prority
      try: h_len = redis.llen(f"tasks:{TaskPriority.HIGH}:{u.id}")
      except Exception as e:
        print(e)
        return

      if h_len != 0:
        # Handle high task offload
        # ? Handle all high prority tasks,
        # TODO: Possible failure point
        value = str(redis.rpop(f"tasks:{TaskPriority.HIGH}:{u.id}"))
        if value is None: pass
        task, access_token = value.split(":")
        # print("value: ", value)
        # print("task: ", task)
        # print("access_token: ", access_token)
        if task == Tasks.trans_sync.value:
          # TODO: How do i know which bank to get the transactions from
          transaction = get_transaction(access_token)
          print(transaction[0])
      else:
        print("No tasks")

      # Check for tasks of low level pro
      try: l_len = redis.llen(f"tasks:{TaskPriority.LOW}:{u.id}")
      except Exception as e:
        print(e)
        return

      if l_len != 0:
        # Handle low task offload
        # TODO: remove task for list tail (RPOP)
        task = redis.rpop(f"tasks:{TaskPriority.LOW}:{u.id}")
        print(task)
        pass
