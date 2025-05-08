from utils.plaid_utils import create_plaid_client
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from database.postgres.postgres_schema import Account, Institution
from utils.logger import log
from utils.core_utils import invert_amount
from typing import Generator, List
from sqlmodel import Session
from utils.types import PlaidTransaction
from utils.plaid_utils import convert_plaid_response


def get_transactions(access_token:str) -> Generator[List[PlaidTransaction], None, None]:
  """
  Get transactions from Plaid API, and validates the response
  """
  client = create_plaid_client()
  has_more:bool = True
  cursor = ""
  # TODO: Save cursor to institutions table; since access token is associated with institution
  while has_more:
    # print(cursor)
    request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
    try: response: TransactionsSyncResponse = client.transactions_sync(request)
    except Exception as e:
      log.error(f"Error getting transactions: {e}")
      return None
    assert isinstance(response, TransactionsSyncResponse)
    # Convert plaid response
    try: converted_response = convert_plaid_response(response)
    except Exception as e:
      log.error(e)
      return None
    has_more = converted_response.has_more
    cursor = converted_response.next_cursor
    yield converted_response.added


def generate_transaction(transactions, db:Session) -> Generator[List[str], None, None]:
  """
  Generates Transaction objects from the transactions gotten from plaid
  and yields a single transaction at a time

  Amount rules:{
    Money leaving the account is positive converted to negative
    Money coming into the account is negative converted to positive
  }
  """
  print("transaction length: ", len(transactions))

  for t in transactions:
    try: acc = db.get(Account, t.account_id)
    except Exception as e:
      log.error(f"Error getting account: {e}")
      continue

    if acc is None:
      log.error("Account not found in database")
      continue

    try: ins = db.get(Institution, acc.institution_id)
    except Exception as e:
      log.error(f"Error getting institution: {e}")
      continue

    if ins is None:
      log.error("Institution not found in database")
      continue

    merchant_name: str = t.merchant_name or t.name
    amount: str = str(invert_amount(t.amount))
    date = t.date.isoformat() if t.date else ""
    authorized_date = t.authorized_date.isoformat() if t.authorized_date else ""
    category = t.personal_finance_category.detailed or ""

    transaction: list[str] = [
      str(t.transaction_id), date, amount, ins.name, acc.name, acc.subtype, category,
      str(t.payment_channel), merchant_name, t.iso_currency_code, str(t.pending), authorized_date
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
