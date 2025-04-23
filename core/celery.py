from utils.plaid_utils import create_plaid_client
from plaid.model.transactions_sync_request import TransactionsSyncRequest

def get_transaction(access_token: str):
  client = create_plaid_client()
  request = TransactionsSyncRequest(
      access_token=access_token,
  )
  # TODO: Possible failure point
  response = client.transactions_sync(request)
  transactions = response['added']
  return transactions
