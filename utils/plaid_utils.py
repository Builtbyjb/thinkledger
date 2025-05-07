import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from utils.types import PlaidResponse, Account, PlaidTransaction, RemovedTransaction, Balances, \
                        PersonalFinanceCategory, PaymentMeta, Location, Counterparty
import os
from typing import List


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


def convert_accounts(accounts) -> List[Account]:
  converted_accounts: List[Account] = []
  for a in accounts:
    acc = Account(
      account_id=a.account_id,
      balances=Balances(
        available=a.balances.available,
        current=a.balances.current,
        iso_currency_code=a.balances.iso_currency_code,
        limit=a.balances.limit,
        unofficial_currency_code=a.balances.unofficial_currency_code
      ),
      mask=a.mask,
      name=a.name,
      official_name=a.official_name,
      subtype=str(a.subtype),
      type=str(a.type)
    )
    converted_accounts.append(acc)
  return converted_accounts


def convert_removed(ids) -> List[RemovedTransaction]:
  removed: List[RemovedTransaction] = []
  for i in ids:
    r = RemovedTransaction(
      account_id=i.account_id,
      transaction_id=i.transaction_id
    )
    removed.append(r)
  return removed


def convert_transactions(transactions) -> List[PlaidTransaction]:
  converted_transactions: List[PlaidTransaction] = []
  for transaction in transactions:
    counter_parties: List[Counterparty] = []
    for counter_party in transaction.counterparties:
      c = Counterparty(
        confidence_level=counter_party.confidence_level,
        entity_id=counter_party.entity_id,
        logo_url=counter_party.logo_url,
        name=counter_party.name,
        phone_number=counter_party.phone_number,
        type=str(counter_party.type),
        website=counter_party.website
      )
      counter_parties.append(c)

    t = PlaidTransaction(
      account_id=transaction.account_id,
      account_owner=transaction.account_owner,
      amount=transaction.amount,
      authorized_date=transaction.authorized_date,
      authorized_datetime=transaction.authorized_datetime,
      category=transaction.category,
      category_id=transaction.category_id,
      check_number=transaction.check_number,
      counterparties=counter_parties,
      date=transaction.date,
      datetime=transaction.datetime,
      iso_currency_code=transaction.iso_currency_code,
      location=Location(
        address=transaction.location.address,
        city=transaction.location.city,
        country=transaction.location.country,
        lat=transaction.location.lat,
        lon=transaction.location.lon,
        postal_code=transaction.location.postal_code,
        region=transaction.location.region,
        store_number=transaction.location.store_number
      ),
      logo_url=transaction.logo_url,
      merchant_entity_id=transaction.merchant_entity_id,
      merchant_name=transaction.merchant_name,
      name=transaction.name,
      payment_channel=transaction.payment_channel,
      payment_meta=PaymentMeta(
        by_order_of=transaction.payment_meta.by_order_of,
        payee=transaction.payment_meta.payee,
        payer=transaction.payment_meta.payer,
        payment_method=transaction.payment_meta.payment_method,
        payment_processor=transaction.payment_meta.payment_processor,
        ppd_id=transaction.payment_meta.ppd_id,
        reason=transaction.payment_meta.reason,
        reference_number=transaction.payment_meta.reference_number
      ),
      pending=transaction.pending,
      pending_transaction_id=transaction.pending_transaction_id,
      personal_finance_category=PersonalFinanceCategory(
        confidence_level=transaction.personal_finance_category.confidence_level,
        detailed=transaction.personal_finance_category.detailed,
        primary=transaction.personal_finance_category.primary
      ),
      personal_finance_category_icon_url=transaction.personal_finance_category_icon_url,
      transaction_code=transaction.transaction_code,
      transaction_id=transaction.transaction_id,
      transaction_type=transaction.transaction_type,
      unofficial_currency_code=transaction.unofficial_currency_code,
      website=transaction.website
    )
    converted_transactions.append(t)
  return converted_transactions


def convert_plaid_response(response: TransactionsSyncResponse) -> PlaidResponse:
  """
  Converts a plaid response type of TransactionsSyncResponse to an internal type of PlaidResponse
  """

  return PlaidResponse(
    accounts=convert_accounts(response.accounts),
    added=convert_transactions(response.added),
    removed=convert_removed(response.removed),
    modified=convert_transactions(response.modified),
    has_more=response.has_more,
    next_cursor=response.next_cursor,
    request_id=response.request_id,
    transactions_update_status=str(response.transactions_update_status),
  )
