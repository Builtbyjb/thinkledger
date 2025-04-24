from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import JSONResponse
from utils.plaid_utils import create_plaid_client
from plaid.model.link_token_create_request import LinkTokenCreateRequest # type: ignore
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser # type: ignore
from plaid.model.products import Products # type: ignore
from plaid.model.link_token_transactions import LinkTokenTransactions # type: ignore
from plaid.model.link_token_account_filters import LinkTokenAccountFilters # type: ignore
from plaid.model.depository_filter import DepositoryFilter # type: ignore
from plaid.model.credit_filter import CreditFilter # type: ignore
from plaid.model.country_code import CountryCode # type: ignore
from plaid.model.depository_account_subtype import DepositoryAccountSubtype # type: ignore
from plaid.model.depository_account_subtypes import DepositoryAccountSubtypes # type: ignore
from plaid.model.credit_account_subtypes import CreditAccountSubtypes # type: ignore
from plaid.model.credit_account_subtype import CreditAccountSubtype # type: ignore
import os
from database.redis.redis import get_redis
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest  # type: ignore
from pydantic import BaseModel
from typing import Optional
from database.postgres.postgres_db import get_db
from database.postgres.postgres_schema import Institution, Account
from utils.core_utils import add_tasks, TaskPriority, Tasks
from sqlmodel import select


router = APIRouter()

class AccountResponse(BaseModel):
  id: str
  name: str
  mask: str
  type: str
  subtype: str
  class_type: Optional[str]
  verification_status: Optional[str]

class InstitutionResponse(BaseModel):
  institution_id: str
  name: str

class PlaidResponse(BaseModel):
  public_token: str
  accounts: list[AccountResponse]
  institution: InstitutionResponse

@router.get("/plaid-link-token")
async def plaid_link_token(request: Request, redis=Depends(get_redis)) -> JSONResponse:
  """
    Get plaid link token to start the institution linking process
  """
  SERVER_URL = os.getenv("SERVER_URL")

  session_id = request.cookies.get('session_id')
  if session_id is None:
    # Should redirect user to the home page
    print("Session ID not found")
    return JSONResponse(content={"error": "Session ID not found"}, status_code=400)

  try: user_id = str(redis.get(session_id))
  except Exception as e:
    print(e)
    return JSONResponse(content={"error":"Internal server error"}, status_code=500)

  link_request = LinkTokenCreateRequest(
    user=LinkTokenCreateRequestUser(client_user_id=user_id),
    client_name='ThinkLedger',
    products=[Products('transactions')],
    transactions=LinkTokenTransactions(days_requested=50),
    country_codes=[CountryCode('US'), CountryCode('CA')],
    language='en',
    webhook=f"{SERVER_URL}/plaid-webhooks",
    # redirect_uri=f"{SERVER_URL}/auth/plaid/callback",
    account_filters=LinkTokenAccountFilters(
      depository=DepositoryFilter(
        account_subtypes=DepositoryAccountSubtypes([
           DepositoryAccountSubtype('checking'),
           DepositoryAccountSubtype('savings')
        ])
      ),
      credit=CreditFilter(
        account_subtypes=CreditAccountSubtypes([CreditAccountSubtype('credit card')])
      )
    )
  )
  client = create_plaid_client()
  try: response = client.link_token_create(link_request)
  except Exception as e:
    print(f"Error creating link token: {e}")
    return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
  # print(response['link_token'])
  return JSONResponse(content={"linkToken": response["link_token"]}, status_code=200)

@router.post("/plaid-access-token")
async def plaid_access_token(
  request: Request,
  data: PlaidResponse,
  db = Depends(get_db),
  redis= Depends(get_redis)
) -> JSONResponse:
  """
    Get an institution's access token with a public token,
    and save the institutions metadata to a database
  """
  exchange_request = ItemPublicTokenExchangeRequest(public_token=data.public_token)
  client = create_plaid_client()
  try:
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response['access_token']
  except Exception as e:
    print(f"Error exchanging public token: {e}")
    return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

  session_id = request.cookies.get("session_id")
  user_id = str(redis.get(session_id))
  if user_id is None:
    print("User not found")
    return JSONResponse(content={"error": "User not found"},status_code=404)
  # print(access_token)

  # Save Institution
  # TODO: Use fastapi background tasks to save institution and accounts
  try:
    """
      Check if institution already exists; if it does, update the access token and
      remove old accounts information.
    """
    ins = db.get(Institution, data.institution.institution_id)
    if ins is None:
      new_ins = Institution(
        id=data.institution.institution_id,
        user_id=user_id,
        name=data.institution.name,
        access_token=access_token
      )
      db.add(new_ins)
      db.commit()
      db.refresh(new_ins)
    else: 
      # Delete old accounts information
      statement = select(Account).where(Account.institution_id == data.institution.institution_id)
      accounts = db.exec(statement).all()
      for account in accounts:
        db.delete(account)
      # Update access token
      ins.access_token = access_token
      db.add(ins)
      db.commit()
      db.refresh(ins)
  except Exception as e:
    print(f"Error saving institution: {e}")
    return JSONResponse(content={"error": "Internal server error"}, status_code=500)

  # Save accounts
  try:
    for a in data.accounts:
      new_acc = Account(
        id=a.id,
        user_id=user_id,
        institution_id=data.institution.institution_id,
        name=a.name,
        subtype=a.subtype,
        type=a.type
      )
      db.add(new_acc)
      db.commit()
      db.refresh(new_acc)
  except Exception as e:
    print(f"Error saving accounts: {e}")
    return JSONResponse(content={"error": "Internal server error"}, status_code=500)

  # Add transaction sync to user task queue
  value = f"{Tasks.trans_sync.value}:{access_token}" # access token holds the institution information
  is_added = add_tasks(value, user_id, TaskPriority.HIGH)
  if is_added is False:
    print("Error adding tasks @plaid-access-token > plaid.py")
    return JSONResponse(content={"error": "Internal server error"}, status_code=500)

  return JSONResponse(content={"message": "Institution and Accounts linked"}, status_code=200)

@router.post("/plaid-webhooks")
async def plaid_webhooks():
  return Response(status_code=200)

@router.get("/auth/plaid/callback")
async def plaid_callback():
  return True


@router.delete("/plaid-account-remove")
async def plaid_account_remove():
  pass

@router.delete("/plaid-account-remove-all")
async def plaid_account_remove_all():
  pass