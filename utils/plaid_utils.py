import plaid # type: ignore
from plaid.api import plaid_api #type: ignore
import os


def create_plaid_client() -> plaid_api.PlaidApi:
  plaid_env = os.getenv("PLAID_ENV")
  plaid_client_id = os.getenv("PLAID_CLIENT_ID")
  plaid_client_secret = os.getenv("PLAID_CLIENT_SECRET")

  host=plaid.Environment.Sandbox
  if plaid_env == "production": host=plaid.Environment.Production
  config = plaid.Configuration(
    host=host,
    api_key={'clientId': plaid_client_id, 'secret': plaid_client_secret})
  api_client = plaid_api.ApiClient(config)
  return plaid_api.PlaidApi(api_client)
