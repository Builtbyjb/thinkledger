from core.google_core import create_service, create_folder
from utils.logger import log
from database.redis.redis import gen_redis

def add_transaction(transaction, user_id: str):
  s_service, d_service = create_service(user_id)
  if s_service is None or d_service is None:
    log.error("Error creating Google Sheets or Google Drive service")
    return

  redis = gen_redis()
  if redis is None:
    log.error("Error getting redis instance")
    return

  # Get parent folder id or create it if it doesn't exist
  try: parent_id = str(redis.get(f"thinkledger:{user_id}"))
  except Exception as e:
    log.error("Error getting thinkledger folder id from redis: ", e)
    return

  if parent_id is None:
    parent_id = create_folder(d_service, "thinkledger", user_id)
    if parent_id is None:
      log.error("Error creating thinkledger folder")
      return

  # Get general ledger folder id or create it if it doesn't exist
  try: general_ledger_id = redis.get(f"general_ledger:{user_id}")
  except Exception as e:
    log.error("Error getting general ledger folder id from redis: ", e)
    return

  if general_ledger_id is None:
    general_ledger_id = create_folder(d_service, "general_ledger", user_id, parent_id)
    if general_ledger_id is None:
      log.error("Error creating general ledger folder")
      return

  # TODO: Create a spreadsheet file in the general ledger folder for the year if it doesn't exist
  # TODO: Create a a transaction sheet in the spreadsheet file, if it doesn't exist
  print(transaction)