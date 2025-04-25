from utils.plaid_utils import create_plaid_client
from plaid.model.transactions_sync_request import TransactionsSyncRequest # type: ignore

def get_transactions(access_token: str):
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