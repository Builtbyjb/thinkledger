from database.postgres.postgres_db import gen_db
from database.redis.redis import gen_redis
from database.postgres.postgres_schema import User, Institution
from sqlmodel import select, Session
from utils.auth_utils import refresh_access_token, verify_access_token
from utils.core_utils import TaskPriority, Tasks
from utils.logger import log
from redis import Redis
import os, sys
from concurrent.futures import ThreadPoolExecutor
from google.google_sheet import GoogleSheet


def handle_high_task(db:Session, redis:Redis, user_id:str) -> None:
  # Check for tasks of High level priority
  try: l = redis.llen(f"tasks:{TaskPriority.HIGH}:{user_id}")
  except Exception as e:
    log.error(f"Error getting high priority tasks length from redis: {e}")
    return None
  if not isinstance(l, int): raise ValueError("Task length must be an integer")

  if l == 0:
    log.info("No high priority tasks")
    return None

  for _ in range(l):
    try: value = redis.rpop(f"tasks:{TaskPriority.HIGH}:{user_id}")
    except Exception as e:
      log.error(f"Error popping high priority task from redis: {e}")
      return None

    if value is not None:
      if not isinstance(value, str): raise ValueError("Value must be a string")
      # NOTE: Rethink how value is handled
      task, _ = value.split(":")

      if task == Tasks.trans_sync.value:
        try:
          google_sheet = GoogleSheet(redis=redis, user_id=user_id, init=True)
          print(google_sheet.spreadsheet_url)
          # TODO: Email spreadsheet_url to the user
        except Exception as e:
          # TODO: if GoogleSheet instantiation fails send an email to the developer
          # and notify the user via email.
          log.error(e)

      # TODO: Created a new task to handle this

        # for t in get_transactions(access_token):
        #   for g in generate_transaction(t, db):
        #     pass
            # is_added = transaction_sheet.append_line([g])
            # if not is_added: log.error("Error creating transaction")

  return None


def handle_low_task(redis:Redis, user_id:str) -> None:
  # Check for tasks of low level priority
  try: l = redis.llen(f"tasks:{TaskPriority.LOW}:{user_id}")
  except Exception as e:
    log.error(f"Error getting low priority tasks from redis: {e}")
    return

  if l != 0:
    # Handle low task offload
    try: task = redis.rpop(f"tasks:{TaskPriority.LOW}:{user_id}")
    except Exception as e:
      log.error(e)
      return
    assert isinstance(task, str) # lazy fix
    print(task)
  return


def check_requirements(db:Session, redis:Redis, user_id:str) -> bool:
  """
  For the requirements function to pass a user needs to connect at least one bank, and
  Grant access to google drive and google sheets.
  """
  # TODO: Check is the user has "Google App Script" enabled

  # Check for institutions
  try: ins = db.exec(select(Institution)).all()
  except Exception as e:
    log.error(f"Error getting institutions from database: {e}")
    return False

  if len(ins) == 0:
    log.info("No institutions")
    return False

  # Check for google workspace access
  try: access_token = redis.get(f"service_access_token:{user_id}")
  except Exception as e:
    log.error(f"Error getting service tokens from redis: {e}")
    return False

  if access_token is None:
    log.error("Error getting access token")
    return False
  # Verify access_token
  if not verify_access_token(str(access_token)):
    # Try refreshing access token if verification fails
    try: refresh_token = redis.get(f"service_refresh_token:{user_id}")
    except Exception as e:
      log.error(f"Error getting service refresh token from redis: {e}")
      return False

    if refresh_token is None:
      log.info("Access token is expired and no refresh token found")
      return False

    client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
    if client_secret is None: raise ValueError ("Google service client ID not found")
    if client_id is None: raise ValueError("Google service client secret not found")

    new_access_token = refresh_access_token(str(refresh_token), client_id, client_secret)
    if new_access_token is None:
      log.error("Failed to refresh access token")
      return False

    # Save new access token
    try: redis.set(f"service_access_token:{user_id}", new_access_token)
    except Exception as e:
      log.error(f"Error setting new service access token in redis: {e}")
      return False
  return True


def handle_task(db:Session, redis:Redis, user_id:str) -> None:
  is_passed =  check_requirements(db, redis, user_id)
  if is_passed:
    handle_high_task(db, redis, user_id)
    handle_low_task(redis, user_id)
  else:
    # TODO: Alert user to complete requirement
    log.info("User did not pass requirement")
  return None


MAX_WORKERS:int = 5
INTERVAL:int = 60 # Secs


def main() -> None:
  """
  Gets users from the database and creates a new thread for each user to handle their tasks.
  """
  log.info("Starting core process...")
  while 1:
    try:
      # Get a fresh DB connection each time through the loop
      db = gen_db()
      if db is None: raise Exception("Failed to get database connection")

      # Get a fresh Redis connection each time through the loop
      redis = gen_redis()
      if redis is None: raise Exception("Failed to get Redis connection")

      users = db.exec(select(User)).all()
      if len(users) == 0: log.info("No users found in database")
      else:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
          futures = {executor.submit(handle_task, db, redis, u.id): u for u in users}
          for f in futures: f.result()
    except KeyboardInterrupt:
      print("Shutting down")
      sys.exit(0)
    except Exception as e: log.error(e)
    finally: break


if __name__ == "__main__":
  main()