from utils.plaid_utils import create_plaid_client
from plaid.model.transactions_sync_request import TransactionsSyncRequest # type: ignore
from database.postgres.postgres_db import gen_db
from database.postgres.postgres_schema import Account, Institution
from utils.logger import log
from utils.core_utils import invert_amount
from typing import Generator, Any


def get_transactions(access_token: str) -> Generator[Any, Any, None]:
  client = create_plaid_client()
  has_more: bool = True
  cursor = ""
  # TODO: Save cursor to institutions table; since access token is associated with institution
  while has_more:
    # print(cursor)
    request = TransactionsSyncRequest(access_token=access_token,cursor=cursor)
    try: response = client.transactions_sync(request)
    except Exception as e:
      log.error(f"Error getting transactions: {e}")
      yield None
      break  # Exit the loop if there's an error
    # TODO: Create response type
    yield response['added']
    has_more = response['has_more']
    cursor = response['next_cursor']


def generate_transaction(transactions) -> Generator[list[str], Any, None]:
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

    merchant_name: str = t.merchant_name or t.name

    amount: str = str(invert_amount(t.amount))

    transaction: list[str] = [
      str(t.transaction_id), t.date.isoformat(), amount, ins.name, acc.name, acc.subtype,
      str(t.category), str(t.payment_channel), merchant_name, t.iso_currency_code, str(t.pending),
      t.authorized_date.isoformat()
    ]

    yield transaction


def get_balance() -> None:
  """
  Gets all the balances of accounts associated with a users connected insitution
  """
  client =  create_plaid_client()
  # Make the request to get the account balance
  try:
    response = client.Accounts.balance.get('your_access_token')
    accounts = response['accounts']
    for account in accounts:
      print(f"Account ID: {account['account_id']}")
      print(f"Available Balance: {account['balances']['available']}")
      print(f"Current Balance: {account['balances']['current']}")
  except Exception as e:
    print(f"An error occurred: {e}")

  return None
