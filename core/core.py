from database.postgres.postgres_db import gen_db
from database.redis.redis import gen_redis
from database.postgres.postgres_schema import User
from sqlmodel import select
from utils.core_utils import TaskPriority, Tasks
from core.plaid_core import get_transactions, generate_transaction
from utils.logger import log
from concurrent.futures import ThreadPoolExecutor
from core.celery import add_transaction
import asyncio


async def handle_high_task(redis, user_id: str) -> None:
  # Check for tasks of High level priority
  try: h_len = redis.llen(f"tasks:{TaskPriority.HIGH}:{user_id}")
  except Exception as e:
    log.error(e)
    return

  if h_len != 0:
    # ? Handle all high priority tasks,
    try: value = str(redis.rpop(f"tasks:{TaskPriority.HIGH}:{user_id}"))
    except Exception as e:
      log.error(e)
      return

    if value is None: pass
    task, access_token = value.split(":")
    # print("value: ", value)
    # print("task: ", task)
    # print("access_token: ", access_token)
    if task == Tasks.trans_sync.value:
      for t in get_transactions(access_token):
        if t is None: continue
        for g in generate_transaction(t):
          await add_transaction(g, user_id)
  else:
    print("No tasks")
  return


def handle_low_task(redis, user_id: str) -> None:
  # Check for tasks of low level priority
  try: l_len = redis.llen(f"tasks:{TaskPriority.LOW}:{user_id}")
  except Exception as e:
    log.error(e)
    return

  if l_len != 0:
    # Handle low task offload
    try: task = redis.rpop(f"tasks:{TaskPriority.LOW}:{user_id}")
    except Exception as e:
      log.error(e)
      return
    print(task)
  return


async def handle_task(redis, user_id: str) -> None:
  await handle_high_task(redis, user_id)
  handle_low_task(redis, user_id)

MAX_WORKERS = 5
INTERVAL = 60


async def core(exit_thread) -> None:
  """
  Gets users from the database and creates a new thread for each user to handle their tasks.
  """
  log.info("Print starting core thread...")

  db = gen_db()
  if db is None: return

  redis = gen_redis()
  if redis is None: return

  with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    while not exit_thread.is_set():
      # time.sleep(60)
      users = db.exec(select(User)).all()
      if users:
        tasks = [asyncio.create_task(handle_task(redis, u.id)) for u in users]
        await asyncio.gather(*tasks)
        # _ = {executor.submit(handle_task, redis, u.id): u for u in users}
        # Wait for all tasks to complete
        # for future in futures:
        #     try:
        #         result = future.result()
        #         # TODO: Process result
        #     except Exception as e:
        #         user = futures[future]
        #         print(f"Task for user {user.id} generated an exception: {e}")
      exit_thread.wait(INTERVAL)

