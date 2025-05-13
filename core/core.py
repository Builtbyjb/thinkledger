from database.postgres.postgres_db import gen_db
from database.redis.redis import gen_redis
from database.postgres.postgres_schema import User, Institution
from sqlmodel import select, Session
from utils.auth_utils import refresh_access_token, verify_access_token
from utils.core_utils import TaskPriority, Tasks
from core.plaid_core import get_transactions, generate_transaction
from utils.logger import log
from core.celery import add_transaction, add_journal_entry
from redis import Redis
from concurrent.futures import ThreadPoolExecutor
import os
from multiprocessing.synchronize import Event


MAX_WORKERS = 5
INTERVAL = 60


def handle_high_task(db: Session, redis: Redis, user_id: str) -> None:
  # Check for tasks of High level priority
  try: len = redis.llen(f"tasks:{TaskPriority.HIGH}:{user_id}")
  except Exception as e:
    log.error(f"Error getting high priority tasks length from redis: {e}")
    return None
  assert isinstance(len, int)

  if len == 0:
    log.info("No high priority tasks")
    return None

  for _ in range(len):
    try: value = redis.rpop(f"tasks:{TaskPriority.HIGH}:{user_id}")
    except Exception as e:
      log.error(f"Error popping high priority task from redis: {e}")
      return None

    if value is not None:
      assert isinstance(value, str)
      # NOTE: Rethink how value is handled
      task, access_token = value.split(":")

      if task == Tasks.trans_sync.value:
        for t in get_transactions(access_token):
          for g in generate_transaction(t, db):
            celery_task1 = add_transaction.delay(g, user_id)
            celery_task1.get() #  Wait for celery tasks
            celery_task2 = add_journal_entry.delay(g, user_id)
            celery_task2.get()


def handle_low_task(redis: Redis, user_id: str) -> None:
  # Check for tasks of low level priority
  try: len = redis.llen(f"tasks:{TaskPriority.LOW}:{user_id}")
  except Exception as e:
    log.error(f"Error getting low priority tasks from redis: {e}")
    return

  if len != 0:
    # Handle low task offload
    try: task = redis.rpop(f"tasks:{TaskPriority.LOW}:{user_id}")
    except Exception as e:
      log.error(e)
      return
    print(task)
  return


def check_requirements(db: Session, redis: Redis, user_id: str) -> bool:
  """
  For the requirements function to pass a user needs to connect at least one bank, and
  Grant access to google drive and google sheets.
  """
  # Check Institution
  try: ins = db.exec(select(Institution)).all()
  except Exception as e:
    log.error(f"Error getting institutions from database: {e}")
    return False

  if len(ins) == 0:
    log.info("No institutions")
    return False

  # Check Scopes
  try: access_token = redis.get(f"service_access_token:{user_id}")
  except Exception as e:
    log.error(f"Error getting service tokens from redis: {e}")
    return False

  if access_token is None: return False
  assert isinstance(access_token, str)

  # Verify access_token
  if not verify_access_token(access_token):
    # Try refreshing access token if verification fails
    try: refresh_token = redis.get(f"service_refresh_token:{user_id}")
    except Exception as e:
      log.error(f"Error getting service refresh token from redis: {e}")
      return False
    if refresh_token is None: return False
    assert isinstance(refresh_token, str)

    client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
    assert client_secret is not None, "Google service client ID is not set"
    assert client_id is not None, "Google service client secret is not set"

    new_access_token, is_refreshed = refresh_access_token(refresh_token, client_id, client_secret)
    if not is_refreshed or new_access_token is None:
      log.error("Failed to refresh access token")
      return False

    try: redis.set(f"service_access_token:{user_id}", new_access_token)
    except Exception as e:
      log.error(f"Error setting service access token in redis: {e}")
      return False
  return True


def handle_task(db: Session, redis: Redis, user_id: str) -> None:
  is_passed =  check_requirements(db, redis, user_id)
  # TODO: Alert user to complete requirements
  if not is_passed: return
  handle_high_task(db, redis, user_id)
  handle_low_task(redis, user_id)


def core(exit_process: Event) -> None:
  """
  Gets users from the database and creates a new thread for each user to handle their tasks.
  """
  log.info("Starting core process...")
  while not exit_process.is_set():
    # Get a fresh DB connection each time through the loop
    db = gen_db()
    if db is None: raise Exception("Failed to get database connection")

    # Get a fresh Redis connection each time through the loop
    redis = gen_redis()
    if redis is None: raise Exception("Failed to get Redis connection")

    # time.sleep(60)
    users = db.exec(select(User)).all()
    if len(users) == 0: log.info("No users found in database")
    else:
      with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        _ = {executor.submit(handle_task, db, redis, u.id): u for u in users}
        # Wait for all tasks to complete
        # for future in futures:
        #     try:
        #         result = future.result()
        #         # TODO: Process result
        #     except Exception as e:
        #         user = futures[future]
        #         print(f"Task for user {user.id} generated an exception: {e}")
    exit_process.wait(INTERVAL)
