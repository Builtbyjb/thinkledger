from core.google_core import create_google_service
from utils.types import Transaction
from database.postgres.postgres_db import gen_db
from database.postgres.postgres_schema import Account, Institution
from utils.core_utils import invert_amount


def add_transaction_to_google_sheet(transactions, user_id: str) -> bool:
  """
  Amount rules:{
    Money leaving the account is positive converted to negative
    Money coming into the account is negative converted to positive
  }
  """
  db = gen_db()
  if db is None: return False

  print("transaction length: ", len(transactions))

  sheets_service, drive_service = create_google_service(user_id)
  if sheets_service is None or drive_service is None:
    print("Error creating Google Sheets service or Google Drive service")
    return False

  # TODO: Create a google drive folder called thinkledger if it doesn't exist
  # TODO: Create a general ledger subfolder in the thinkledger folder, if it doesn't exist
  # TODO: Create a spreadsheet file in the general ledger folder for the year if it doesn't exist
  # TODO: Create a a transaction sheet in the spreadsheet file, if it doesn't exist

  for t in transactions:
    acc = db.get(Account, t.account_id)
    if acc is None:
      print("Account not found in database")
      return False
    
    ins = db.get(Institution, acc.institution_id)
    if ins is None:
      print("Institution not found in database")
      return False

    merchant_name = t.merchant_name
    if t.merchant_name is None: merchant_name = t.name

    amount = invert_amount(t.amount)

    transaction = Transaction(
      id=t.transaction_id,
      date=t.date, 
      amount=amount,
      institution=ins.name,
      institution_account_name=acc.name,
      institution_account_type=acc.subtype,
      category=t.category,
      payment_channel=t.payment_channel,
      merchant_name=merchant_name,
      currency_code=t.iso_currency_code,
      pending=t.pending,
      authorized_date=t.authorized_date
    )

    # TODO: Add transaction to google sheet

    # print(transaction)

  return True