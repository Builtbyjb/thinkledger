from pydantic import BaseModel
from datetime import date as dt, datetime as dtt
from typing import List, Optional


# class Transaction(BaseModel):
#   id: str
#   date: dt
#   amount: float
#   institution: str
#   institution_account_name: str
#   institution_account_type: str
#   category: str
#   payment_channel: str
#   merchant_name: str
#   currency_code: str
#   pending: bool
#   authorized_date: Optional[dt]


class Counterparty(BaseModel):
  confidence_level: str
  entity_id: Optional[str]
  logo_url: Optional[str]
  name: str
  phone_number: Optional[str]
  type: str
  website: Optional[str]


class Location(BaseModel):
  address: Optional[str]
  city: Optional[str]
  country: Optional[str]
  lat: Optional[float]
  lon: Optional[float]
  postal_code: Optional[str]
  region: Optional[str]
  store_number: Optional[str]


class PaymentMeta(BaseModel):
  by_order_of: Optional[str]
  payee: Optional[str]
  payer: Optional[str]
  payment_method: Optional[str]
  payment_processor: Optional[str]
  ppd_id: Optional[str]
  reason: Optional[str]
  reference_number: Optional[str]


class PersonalFinanceCategory(BaseModel):
  confidence_level: str
  detailed: str
  primary: str


class PlaidTransaction(BaseModel):
  account_id: str
  account_owner: Optional[str]
  amount: float
  authorized_date: Optional[dt]
  authorized_datetime: Optional[dtt]
  category: Optional[str]
  category_id: Optional[str]
  check_number: Optional[str]
  counterparties: List[Counterparty]
  date: dt
  datetime: Optional[dtt]
  iso_currency_code: str
  location: Location
  logo_url: Optional[str]
  merchant_entity_id: Optional[str]
  merchant_name: Optional[str]
  name: str
  payment_channel: str
  payment_meta: PaymentMeta
  pending: bool
  pending_transaction_id: Optional[str]
  personal_finance_category: PersonalFinanceCategory
  personal_finance_category_icon_url: str
  transaction_code: Optional[str]
  transaction_id: str
  transaction_type: str
  unofficial_currency_code: Optional[str]
  website: Optional[str]


class Balances(BaseModel):
  available: Optional[float]
  current: float
  iso_currency_code: str
  limit: Optional[float]
  unofficial_currency_code: Optional[str]


class Account(BaseModel):
  account_id: str
  balances: Balances
  mask: str
  name: str
  official_name: str
  subtype: str
  type: str


class RemovedTransaction(BaseModel):
  account_id:str
  transaction_id:str


class PlaidResponse(BaseModel):
  accounts:List[Account]
  added:List[PlaidTransaction]
  has_more:bool
  modified:List[PlaidTransaction]
  next_cursor:str
  removed:List[RemovedTransaction]
  request_id:str
  transactions_update_status:str


class JournalAccount(BaseModel):
  name:str
  account_id:str
  amount:str


class JournalEntry(BaseModel):
  date:dt
  description:str
  debit:List[JournalAccount]
  credit:List[JournalAccount]