from pydantic import BaseModel
from datetime import date as dt
from typing import Optional


class Transaction(BaseModel):
  id: str
  date: dt
  amount: float
  institution: str
  institution_account_name: str
  institution_account_type: str
  category: list[str]
  payment_channel: str
  merchant_name: str
  currency_code: str
  pending: bool
  authorized_date: Optional[dt]
