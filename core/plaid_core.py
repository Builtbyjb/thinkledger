from utils.plaid_utils import create_plaid_client
from plaid.model.transactions_sync_request import TransactionsSyncRequest # type: ignore
from utils.types import Transaction
from database.postgres.postgres_db import gen_db
from database.postgres.postgres_schema import Account, Institution
from utils.logger import log
from utils.core_utils import invert_amount
from typing import Generator, Any


def get_transactions(access_token: str) -> Generator[Any, None]:
  client = create_plaid_client()
  has_more: bool = True
  cursor = ""
  # TODO: Save cursor to institutions table; since access token is associated with institution
  while has_more:
    # print(cursor)
    request = TransactionsSyncRequest(access_token=access_token,cursor=cursor)
    try: response = client.transactions_sync(request)
    except Exception as e:
      print("Error getting transactions: ", e)
      yield  None
    response = client.transactions_sync(request)
    yield response['added']
    has_more = response['has_more']
    cursor = response['next_cursor']

def generate_transaction(transactions) -> Generator[Transaction, None]:
  """
  Generates Transaction objects from the transactions gotten from plaid
  and yields a single transaction at a time

  Amount rules:{
    Money leaving the account is positive converted to negative
    Money coming into the account is negative converted to positive
  }
  """
  db = gen_db()
  if db is None: return None

  print("transaction length: ", len(transactions))

  # TODO: Convert transactions to a list following the headers format

  for t in transactions:
    try: acc = db.get(Account, t.account_id)
    except Exception as e:
      log.error(f"Error getting account: {e}")
      return None

    if acc is None:
      log.error("Account not found in database")
      return None

    try: ins = db.get(Institution, acc.institution_id)
    except Exception as e:
      log.error(f"Error getting institution: {e}")
      return None

    if ins is None:
      log.error("Institution not found in database")
      return None

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

    yield transaction