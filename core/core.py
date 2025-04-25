from database.postgres.postgres_db import gen_db
from database.redis.redis import gen_redis
from database.postgres.postgres_schema import User
from sqlmodel import select
import time
from utils.core_utils import TaskPriority, Tasks
from core.celery import add_transaction_to_google_sheet
from core.plaid_core import get_transactions


def handle_high_task(user_id: str):
  pass

def handle_low_task(user_id: str):
  pass

def handle_task(user_id: str):
  pass

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
      # TODO: Split into two functions
      # Check for tasks of High level priority
      try: h_len = redis.llen(f"tasks:{TaskPriority.HIGH}:{u.id}")
      except Exception as e:
        print(e)
        continue

      if h_len != 0:
        # Handle high task offload
        # ? Handle all high priority tasks,
        try: value = str(redis.rpop(f"tasks:{TaskPriority.HIGH}:{u.id}"))
        except Exception as e:
          print(e)
          continue

        if value is None: pass
        task, access_token = value.split(":")
        # print("value: ", value)
        # print("task: ", task)
        # print("access_token: ", access_token)
        if task == Tasks.trans_sync.value:
          for t in get_transactions(access_token):
            if t is None:
              print("Error getting transactions")
              continue
            else:
              if not add_transaction_to_google_sheet(t, u.id):
                print("Error adding transaction to google sheet")
                continue
      else:
        print("No tasks")

      # Check for tasks of low level priority
      try: l_len = redis.llen(f"tasks:{TaskPriority.LOW}:{u.id}")
      except Exception as e:
        print(e)
        return

      if l_len != 0:
        # Handle low task offload
        try: task = redis.rpop(f"tasks:{TaskPriority.LOW}:{u.id}")
        except Exception as e:
          print(e)
          continue
        print(task)

