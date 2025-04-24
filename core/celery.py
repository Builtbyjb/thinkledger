from utils.plaid_utils import create_plaid_client
from plaid.model.transactions_sync_request import TransactionsSyncRequest # type: ignore
from core.google_core import create_google_service
from utils.types import Transaction
from database.postgres.postgres_db import gen_db
from database.postgres.postgres_schema import Account, Institution
from utils.core_utils import invert_amount


def get_transaction(access_token: str):
  client = create_plaid_client()
  request = TransactionsSyncRequest(access_token=access_token)
  try: response = client.transactions_sync(request)
  except Exception as e:
    print("Error getting transactions: ", e)
    return None
  transactions = response['added']
  return transactions

def add_transaction_to_google_sheet(transactions, user_id: str) -> bool:
  """
  Amount rules:{
    Money leaving the account is positive converted to negative
    Money coming into the account is negative converted to positive
  }
  """
  db = gen_db()
  if db is None: return False

  sheets_service, drive_service = create_google_service(user_id)
  if sheets_service is None or drive_service is None:
    print("Error creating Google Sheets service or Google Drive service")
    return False

  for t in transactions:
    # TODO: Fix account mismatch
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

    print(transaction)

  return True