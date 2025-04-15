from fastapi import APIRouter, Response, Request, Depends, HTTPException
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.link_token_transactions import LinkTokenTransactions
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.depository_filter import DepositoryFilter
from plaid.model.credit_filter import CreditFilter
from plaid.model.country_code import CountryCode
from plaid.model.depository_account_subtype import DepositoryAccountSubtype
from plaid.model.depository_account_subtypes import DepositoryAccountSubtypes
from plaid.model.credit_account_subtypes import CreditAccountSubtypes
from plaid.model.credit_account_subtype import CreditAccountSubtype
import os
from database.redis.redis import get_redis_client
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from pydantic import BaseModel

router = APIRouter()

class PlaidResponse(BaseModel):
    public_token: str

def create_plaid_client() -> plaid_api.PlaidApi:
    PLAID_ENV = os.getenv("PLAID_ENV")
    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    PLAID_CLIENT_SECRET = os.getenv("PLAID_CLIENT_SECRET")

    host=plaid.Environment.Sandbox
    if PLAID_ENV == "production":
        host=plaid.Environment.Production

    config = plaid.Configuration(
        host=host,
        api_key={
            'clientId': PLAID_CLIENT_ID,
            'secret': PLAID_CLIENT_SECRET
        }
    )

    api_client = plaid_api.ApiClient(config)
    client = plaid_api.PlaidApi(api_client)
    return client


@router.get("/plaid-link-token")
async def plaid_link_token(request: Request, redis=Depends(get_redis_client)):
    SERVER_URL = os.getenv("SERVER_URL")

    session_id = request.cookies.get('session_id')
    try:
        user_id = redis.get(session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    link_request = LinkTokenCreateRequest(
      user=LinkTokenCreateRequestUser(
        client_user_id=user_id,
      ),
      client_name='ThinkLedger',
      products=[Products('transactions')],
      transactions=LinkTokenTransactions(
        days_requested=100
      ),
      country_codes=[CountryCode('US'), CountryCode('CA')],
      language='en',
      webhook=f"{SERVER_URL}/plaid-webhooks",
      redirect_uri=f"{SERVER_URL}/auth/plaid/callback",
      account_filters=LinkTokenAccountFilters(
        depository=DepositoryFilter(
          account_subtypes=DepositoryAccountSubtypes([
             DepositoryAccountSubtype('checking'),
             DepositoryAccountSubtype('savings')
          ])
        ),
        credit=CreditFilter(
          account_subtypes=CreditAccountSubtypes([
             CreditAccountSubtype('credit card')
          ])
        )
      )
    )

    client = create_plaid_client()
    response = await client.link_token_create(link_request)
    return {"link_token": response["link_token"]}


@router.post("/plaid-access-token")
async def plaid_access_token(request: Request, response: PlaidResponse):
    # Save meta data

    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=response.public_token
    )

    client = create_plaid_client()
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response['access_token']
    print(access_token)
    return {"message": "Access token gotten"}


@router.post("/plaid-webhooks")
async def plaid_webhooks():
    return Response(status_code=200)


@router.get("/auth/plaid/callback")
async def plaid_callback():
    return {"access_token": "example_access_token"}
