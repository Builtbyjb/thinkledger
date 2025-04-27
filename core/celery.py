from celery import Celery
from core.google_core import (
  create_service,
  create_folder,
  create_spreadsheet,
  create_transaction_sheet,
  append_to_sheet
)
from utils.logger import log
from database.redis.redis import gen_redis
from typing import Optional
import os


c = Celery("tasks", broker=os.getenv("REDIS_URL"))

@c.task
async def add_transaction(transaction, user_id: str) -> None:
  s_service, d_service = await create_service(user_id)
  if s_service is None or d_service is None:
    log.error("Error creating Google Sheets or Google Drive service")
    return

  redis = gen_redis()
  if redis is None:
    log.error("Error getting redis instance")
    return

  # Get parent folder id or create it if it doesn't exist
  parent_id: Optional[str] = await redis.get(f"thinkledger:{user_id}")
  if parent_id is None:
    parent_id = create_folder(d_service, "thinkledger", user_id)
    if parent_id is None:
      log.error("Error creating thinkledger folder")
      return

  # Get general ledger folder id or create it if it doesn't exist
  general_ledger_id: Optional[str] = await redis.get(f"general_ledger:{user_id}")
  if general_ledger_id is None:
    general_ledger_id = create_folder(d_service, "general_ledger", user_id, parent_id)
    if general_ledger_id is None:
      log.error("Error creating general ledger folder")
      return

  # Get spreadsheet file id or create it if it doesn't exist
  spreadsheet_id: Optional[str] = await redis.get(f"spreadsheet:{user_id}")
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