from celery import Celery
import os
import sys
from utils.logger import log
from typing import List
from core.google_core import TransactionsSheet, JournalEntrySheet


REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL is None: sys.exit("REDIS_URL environment variable is not set")

c = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@c.task
def add_transaction(transaction:List[str], user_id:str) -> None:
  """
  Add transactions to google sheet.
  """
  transaction_sheet = TransactionsSheet(user_id)
  is_added = transaction_sheet.append(transaction)
  assert is_added is True, "Error appending transaction to sheet"

  # print(transaction)
  log.info("Transaction added successfully")
  return


@c.task
def add_journal_entry(transaction:List[str], user_id:str) -> None:
  """
  Add journal entries to google sheet.
  """
  journal_entry_sheet = JournalEntrySheet(user_id)
  journal_entry = journal_entry_sheet.generate(transaction)
  assert journal_entry is not None
  # is_added = journal_entry_sheet.append(journal_entry)
  # assert is_added is True, "Error appending journal entry to sheet"

  print(journal_entry)
  log.info("Journal entry added successfully")
  return