from celery import Celery
import os
import sys
from utils.logger import log
from typing import List
from core.google_core import create_deps, append_to_sheet, generate_journal_entry, spreadsheet_setup
from utils.constants import TransactionsSheet, JournalEntrySheet
from utils.types import SheetValue


REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL is None: sys.exit("REDIS_URL environment variable is not set")

c = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@c.task
def add_transaction(transaction:List[str], user_id:str) -> None:
  """
  Add transactions to google sheet.
  # NOTE: Need to refactor append to sheet function
  """
  # Create a transaction sheet in the spreadsheet file if it doesn't exist
  transaction_sheet_value = TransactionsSheet()
  sheet_value = SheetValue(**transaction_sheet_value.model_dump())
  is_created, spreadsheet_id, s_service = create_deps(user_id, sheet_value)
  assert is_created is True, "Error creating folders or files"
  assert spreadsheet_id is not None, "Error creating spreadsheet file"

   # Append the transaction to the transaction sheet
  try:
    is_added = append_to_sheet(transaction, s_service,  spreadsheet_id, sheet_value.name)
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
  Create journal entries from transactions and adds them to a "Journal Entries" sheet in the
  spreadsheet file.
  """
  journal_entry_sheet_value = JournalEntrySheet()
  sheet_value = SheetValue(**journal_entry_sheet_value.model_dump())
  is_created, spreadsheet_id, s_service = create_deps(user_id, sheet_value)
  assert is_created is True, "Error creating folders or files"
  assert spreadsheet_id is not None, "Error creating spreadsheet file"

  journal_entry = generate_journal_entry(transaction)
  print(journal_entry)

  # is_added = append_to_sheet(journal_entry, s_service, spreadsheet_id, sheet_value.name)
  # assert is_added is True, "Error appending journal entry to sheet"

  spreadsheet_setup()
  return