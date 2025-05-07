from celery import Celery
from plaid.model.sandbox_payment_simulate_request import sys
from core.google_core import create_service, create_folder, create_spreadsheet, \
                            create_transaction_sheet, append_to_sheet
from utils.logger import log
from database.redis.redis import gen_redis
import os

REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL is None: sys.exit("REDIS_URL environment variable is not set")

c = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


# TODO: Refactor creating folders and spreadsheets should be done once, while appending to
# to a sheet can e done multiple times
@c.task
def add_transaction(transaction, user_id: str) -> None:
  s_service, d_service = create_service(user_id)
  if s_service is None or d_service is None:
    log.error("Error creating Google Sheets or Google Drive service")
    return

  redis = gen_redis()
  if redis is None:
    log.error("Error getting redis instance")
    return

  # Get parent folder id or create it if it doesn't exist
  parent_id = redis.get(f"thinkledger:{user_id}")
  if parent_id is None:
    parent_id = create_folder(d_service, "thinkledger", user_id)
    if parent_id is None:
      log.error("Error creating thinkledger folder")
      return
  assert isinstance(parent_id, str)

  # Get general ledger folder id or create it if it doesn't exist
  general_ledger_id = redis.get(f"general_ledger:{user_id}")
  if general_ledger_id is None:
    general_ledger_id = create_folder(d_service, "general_ledger", user_id, parent_id)
    if general_ledger_id is None:
      log.error("Error creating general ledger folder")
      return
  assert isinstance(general_ledger_id, str)

  # Get spreadsheet file id or create it if it doesn't exist
  spreadsheet_id = redis.get(f"spreadsheet:{user_id}")
  if spreadsheet_id is None:
    spreadsheet_id = create_spreadsheet(
      d_service,
      s_service,
      "ledger_2025",
      general_ledger_id,
      user_id
    )
    if spreadsheet_id is None:
      log.error("Error creating spreadsheet file")
      return
  assert isinstance(spreadsheet_id, str)

  # Create a transaction sheet in the spreadsheet file if it doesn't exist
  try: create_transaction_sheet(s_service, spreadsheet_id)
  except Exception as e:
    log.error("Error creating transaction sheet: ", e)
    return

  # Append the transaction to the transaction sheet
  try:
    is_added = append_to_sheet(transaction,s_service,  spreadsheet_id, "Transactions")
    if not is_added:
      log.error("Error appending transaction to sheet")
      return
  except Exception as e:
    log.error("Error appending transaction to sheet: ", e)
    return

  print(transaction)
  log.info("Transaction added successfully")
  return
