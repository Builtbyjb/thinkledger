from database.postgres.postgres_db import gen_db
from database.redis.redis import gen_redis
from database.postgres.postgres_schema import User, Institution
from sqlmodel import select, Session
from utils.auth_utils import refresh_access_token, verify_access_token
from utils.tasks import TaskPriority, Tasks, get_task, get_task_args
from utils.logger import log
from redis import Redis
import os, sys, time
from concurrent.futures import ThreadPoolExecutor
from google_core.google_sheet import GoogleSheet, TransactionSheet, JournalEntrySheet
from utils.context import DEBUG
from plaid_core.plaid import get_transactions, generate_transaction


# TODO: Rethink this function
async def handle_high_priority_task(db:Session, redis:Redis, user_id:str) -> None:
  # Check for tasks of High level priority
  with redis as r:
    try: l = await r.llen(f"task:{TaskPriority.HIGH.value}:{user_id}")
    except Exception as e:
      log.error(f"Error getting high priority tasks length from redis: {e}")
      return None
  if not isinstance(l, int): raise ValueError("Task length must be an integer")

  if l == 0:
    if DEBUG >= 1: log.info("No high priority tasks")
    return None

  with redis as r:
    for _ in range(l):
      try: value = await r.rpop(f"task:{TaskPriority.HIGH.value}:{user_id}")
      except Exception as e:
        log.error(f"Error popping high priority task from redis: {e}")
        return None

      if value is None: continue
      if DEBUG >= 1: log.info(value)
      if not isinstance(value, str): raise ValueError("Value must be a string")
      task = get_task(value)
      if task == Tasks.setup_spreadsheet.value:
        try:
          google_sheet = GoogleSheet(redis=r, user_id=user_id, init=True)
          if DEBUG >= 1: log.info(google_sheet.spreadsheet_url)
          # TODO: Email spreadsheet_url to the user
        except Exception as e:
          # User email address is stored in redis
          # TODO: if GoogleSheet instantiation fails send an email to the developer
          # and notify the user via email.
          log.error(e)
      elif task == Tasks.sync_transaction.value:
        spreadsheet_id = get_task_args(value)[0]
        if DEBUG >= 1: log.info(spreadsheet_id)
        with db as d:
          ins = d.get(Institution, user_id)
        if ins is None: raise ValueError("Institution not found")
        transaction_sheet = TransactionSheet(r, user_id)
        journal_entry_sheet = JournalEntrySheet(r, user_id)
        for t in get_transactions(ins.access_token):
          for g in generate_transaction(t, db):
            # Add transaction
            is_added_t = transaction_sheet.append_line(spreadsheet_id, [g])
            if not is_added_t: log.error("Error creating transaction")
            # Add journal entry
            journal_entry = journal_entry_sheet.generate(g)
            if journal_entry is None: ValueError("Error creating journal entry")
            assert journal_entry is not None
            is_added_entry = journal_entry_sheet.append_line(spreadsheet_id, journal_entry)
            if not is_added_entry: log.error("Error creating journal entry")

  return None


def handle_low_priority_task(redis:Redis, user_id:str) -> None:
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


async def handle_task(db:Session, redis:Redis, user_id:str) -> None:
  is_passed =  check_requirements(db, redis, user_id)
  if is_passed:
    await handle_high_priority_task(db, redis, user_id)
    handle_low_priority_task(redis, user_id)
  else:
    # TODO: Alert user to complete requirement, Some time as passed
    log.info("User did not pass requirement")
  return None


MAX_WORKERS:int = 5
INTERVAL:float = 0.1 # 100ms


def main() -> None:
  """
  Gets users from the database and creates a new thread for each user to handle their tasks.
  """
  try:
    db = gen_db()
    if db is None: raise Exception("Failed to get database connection")
  except Exception as e:
    log.error(e)
    sys.exit(1)

  try:
    redis = gen_redis()
    if redis is None: raise Exception("Failed to get Redis connection")
  except Exception as e:
    log.error(e)
    sys.exit(1)

  if DEBUG >= 1: log.info("Starting...")

  while 1:
    try:
      users = db.exec(select(User)).all()
      if len(users) == 0:
        if DEBUG >= 1: log.info("No users found in database")
        continue
      with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        _ = {executor.submit(handle_task, db, redis, u.id): u for u in users}

      time.sleep(INTERVAL)
    except KeyboardInterrupt:
      print("\nShutting down")
      sys.exit(0)
    except Exception as e:
      log.error(e)
      sys.exit(1)


if __name__ == "__main__":
  main()
