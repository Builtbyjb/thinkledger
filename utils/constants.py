from pydantic import BaseModel
from typing import List

TOKEN_INFO_URL:str = "https://www.googleapis.com/oauth2/v3/tokeninfo"
TOKEN_URL:str = "https://oauth2.googleapis.com/token"

class TransactionsSheet(BaseModel):
  name:str = "Transactions"
  header:List[str] = [
    'ID', 'Date', 'Amount', 'Institution', 'Institution Account Name', 'Institution Account Type', 
    'Category', 'Payment Channel', 'Merchant Name', 'Currency', 'Pending', 'Authorized Date'
  ]
  range:str = "Transactions!A1:L1"