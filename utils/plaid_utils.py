import plaid
from plaid.api import plaid_api
import os


def create_plaid_client() -> plaid_api.PlaidApi:
  PLAID_ENV = os.getenv("PLAID_ENV")
  PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
  PLAID_CLIENT_SECRET = os.getenv("PLAID_CLIENT_SECRET")

  host=plaid.Environment.Sandbox
  if PLAID_ENV == "production": host=plaid.Environment.Production
  config = plaid.Configuration(
    host=host,
    api_key={
      'clientId': PLAID_CLIENT_ID,
      'secret': PLAID_CLIENT_SECRET
    })
  api_client = plaid_api.ApiClient(config)
  client = plaid_api.PlaidApi(api_client)
  return client
