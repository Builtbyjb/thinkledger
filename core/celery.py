from celery import Celery
import os
import sys
from utils.logger import log
from typing import List
from core.google_core import create_folder, create_service, create_spreadsheet, \
                            create_sheet, append_to_sheet
from datetime import datetime
from utils.constants import TransactionsSheet
from utils.types import SheetValue


REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL is None: sys.exit("REDIS_URL environment variable is not set")

c = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

@c.task
def add_transaction(transaction:List[str], user_id:str) -> None:
  """
  ** NOTE ** 
  this function is almost the same as the add_journal_entry(), is there a way to refactor 
  the function so i do not have to repeat myself.

  I still have to talk to gemini before adding a journal entry adding but the boiler plate of 
  creating a sheet is still the same.

  ideas: 
  * Add spreadsheet headers to the utils constant.py file
  create a sheet object that store the sheet name, header list and header name
  * Refactor create sheet function
  * Refactor append to sheet function

  Add transactions to google sheet
  """
  s_service, d_service = create_service(user_id)
  if s_service is None or d_service is None:
    log.error("Error creating Google Sheets or Google Drive service")
    return

  # Get parent folder id or create it if it doesn't exist
  parent_id = create_folder(d_service, "thinkledger")
  assert isinstance(parent_id, str), "Error creating thinkledger folder"

  # Get general ledger folder id or create it if it doesn't exist
  general_ledger_id = create_folder(d_service, "general_ledger", parent_id)
  assert isinstance(general_ledger_id, str), "Error creating general ledger folder"

  # Get spreadsheet file id or create it if it doesn't exist
  file_name = f"ledger_{datetime.now().year}"
  spreadsheet_id = create_spreadsheet(d_service, s_service, file_name, general_ledger_id)
  assert isinstance(spreadsheet_id, str), "Error creating spreadsheet file"

  # Create a transaction sheet in the spreadsheet file if it doesn't exist
  transaction_sheet_value = TransactionsSheet()
  sheet_value = SheetValue(**transaction_sheet_value.model_dump())
  try: create_sheet(s_service, spreadsheet_id, sheet_value)
  except Exception as e:
    log.error(f"Error creating {sheet_value.name} sheet: {e}")
    return

  # Append the transaction to the transaction sheet
  try:
    is_added = append_to_sheet(transaction, s_service,  spreadsheet_id, "Transactions")
    assert is_added is True, "Error appending transaction to sheet"
  except Exception as e:
    log.error("Error appending transaction to sheet: ", e)
    return

  # print(transaction)
  log.info("Transaction added successfully")
  return
  

@c.task
def add_journal_entry(transaction:List[str], user_id:str) -> None:
  """
  ** NOTE **
  * Create a journal entry sheet.
  * create a transaction object to make it easier for gemini to generate journal entries.
  * convert gemini response to a list of str.
  * Add journal entry to sheet.
  * Call a spreadsheet_setup() function that creates the other sheets and configures them so they 
  are automatically update when when a new journal entry is added.
  """
  return