from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from database.redis.redis import gen_redis
from typing import Optional, Tuple, Any, List
import os
from dataclasses import dataclass
from utils.constants import TOKEN_URL
from utils.logger import log
from datetime import datetime
from prompt.journal_entry import generate_prompt
from agents.gemini import gemini_response, sanitize_gemini_response

"""
NOTE: 
i might need the journal sheet id

TODO: Early return if the folders, files or sheets exists
"""

@dataclass
class GoogleSheet:
  def __init__(self, user_id:str):
    self.user_id = user_id
    self.s_service, self.d_service = self.create_service()
    assert self.s_service is not None and self.d_service is not None
    # Create thinkledger root folder if it doesn't exist
    parent_id = self.create_folder("thinkledger")
    assert isinstance(parent_id, str), "Error creating thinkledger folder"
    # Create general_ledger folder if it doesn't exist
    general_ledger_id = self.create_folder("general_ledger", parent_id)
    assert isinstance(general_ledger_id, str), "Error creating general ledger folder"
    # Create spreadsheet file, if it doesn't exist
    file_name = f"ledger_{datetime.now().year}"
    spreadsheet_id = self.create_spreadsheet(file_name, general_ledger_id)
    assert isinstance(spreadsheet_id, str), "Error creating spreadsheet file"
    self.spreadsheet_id = spreadsheet_id
    # setup transaction sheet
    self.setup_transaction()
    # setup journal entry sheet
    self.setup_journal_entry()
    # setup up  T account sheet
    # setup trial balance sheet
    # setup up financial statements
  
  def create_service(self) -> Tuple[Any, Any]:
    """
    Create a google sheet service and a google drive service; returns None if failed
    """
    redis = gen_redis()
    if redis is None: return None, None

    client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
    assert client_id is not None, "Client ID is not set"
    assert client_secret is not None, "Client secret is not set"

    # Verify access token; and if expired, use refresh token to get new access token
    access_token = redis.get(f"service_access_token:{self.user_id}")
    if access_token is None:
      log.error("Service access token not found in redis")
      return None, None
    assert isinstance(access_token, str), "Access token is not a string"

    refresh_token = redis.get(f"service_refresh_token:{self.user_id}")

    credentials = Credentials(
      token=access_token,
      token_uri=TOKEN_URL,
      refresh_token=refresh_token,
      client_id=client_id,
      client_secret=client_secret,
    )

    try:
      sheets_service = build("sheets", "v4", credentials=credentials)
      drive_service = build("drive", "v3", credentials=credentials)
    except Exception as e:
      log.error(f"Error creating Google Sheets service or Google Drive service: {e}")
      return None, None
    return sheets_service, drive_service

  def create_folder(self, name:str, parent_id:str="root") -> Optional[str]:
    """
    Create a folder in the user's google drive. The parent_id specifies the parent folder id; if it
    is "root", the folder will be created in the root directory.
    """
    try:
      # Check if folder exists
      query = f"""
      name='{name}' and mimeType='application/vnd.google-apps.folder' and
      '{parent_id}' in parents and trashed=false
      """
      results = self.d_service.files().list(q=query).execute()
      items = results.get('files', [])

      # Create folder if it doesn't exist
      if not items:
        metadata = {
          'name': name,
          'mimeType': 'application/vnd.google-apps.folder',
          "parents": [parent_id]
        }

        folder = self.d_service.files().create(body=metadata, fields='id').execute()
        folder_id = folder.get('id')
      else: folder_id = items[0].get('id')
    except Exception as e:
      log.error("Error creating folder: ", e)
      return None
    return folder_id

  def create_spreadsheet(self, name:str, folder_id:str) -> Optional[str]:
    """
    Create a spreadsheet file in a folder
    *** NOTE **
    if spreadsheet file name changes it means the year has changed, write a function that pulls in
    all the relevant data from the pervious year.
    """
    try:
      # Check if spreadsheet exists
      query = f"""
      name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'
      and '{folder_id}' in parents and trashed=false
      """
      results = self.d_service.files().list(q=query).execute()
      files = results.get('files', [])
      if files: return files[0].get('id')

      # Create new spreadsheet
      spreadsheet_body = {'properties': {'title': name}}
      spreadsheet = self.s_service.spreadsheets().create(body=spreadsheet_body).execute()

      # Move to correct folder
      spreadsheet_id = spreadsheet.get('spreadsheetId')
      self.d_service.files().update(
        fileId=spreadsheet_id,
        addParents=folder_id,
        removeParents='root',
        fields='id, parents'
      ).execute()
    except Exception as e:
      log.error(f'Google Sheets API error: {e}')
      return None
    return spreadsheet_id

  def create_sheet(self, name:str, header:List[str], range:str) -> None:
    """
    Create a sheet in the spreadsheet file
    """
    # TODO: Return a sheet id
    try:
      # First, get all sheets in the spreadsheet
      sheet_metadata = self.s_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
      sheets = sheet_metadata.get('sheets', [])

      # Check if sheet already exists
      sheet_exists = any(
        sheet.get('properties', {}).get('title') == name for sheet in sheets
      )
      if not sheet_exists:
        # Create a new sheet
        body = {
          'requests': [{
            'addSheet': {
              'properties': { 'title': name }
            }
          }]
        }

        self.s_service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
        log.info(f"Created new {name} sheet")

        # Update the sheet with headers
        self.s_service.spreadsheets().values().update(
          spreadsheetId=self.spreadsheet_id,
          range=range,
          valueInputOption='RAW',
          body={'values':[header]}
        ).execute()
        log.info(f"Added headers to {name} sheet")
    except Exception as e:
      log.error(f"Error creating {name} sheet: {e}")
    return None
  
  def setup_transaction(self):
    name:str = "Transactions"
    header:List[str] = [
      'ID', 'Date', 'Amount', 'Institution', 'Institution Account Name', 'Institution Account Type',
      'Category', 'Payment Channel', 'Merchant Name', 'Currency', 'Pending', 'Authorized Date'
    ]
    range:str = "Transactions!A1:L1"
    self.create_sheet(name, header, range)
    return

  def setup_journal_entry(self):
    name:str = "Journal Entries"
    header:List[str] = ["Date", "Description", "Account Name", "Account ID", "Debit", "Credit"]
    range:str = "Journal Entries!A1:F1"
    self.create_sheet(name, header, range)
    return

  def setup_t_account(self):
    pass

  def setup_trial_bal(self):
    pass

  def setup_bal_sheet(self):
    pass


@dataclass
class TransactionsSheet(GoogleSheet):
  def __init__(self, user_id:str):
    super().__init__(user_id)
    self.name:str = "Transactions"

  def append(self, transaction) -> bool:
    """
    Append a row to the sheet
    """
    try:
      self.s_service.spreadsheets().values().append(
        spreadsheetId=self.spreadsheet_id,
        range=self.name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': [transaction]}
      ).execute()
    except Exception as e:
      log.error(f"Error appending to sheet: {e}")
      return False
    return True


@dataclass
class JournalEntrySheet(GoogleSheet):
  def __init__(self, user_id:str):
    super().__init__(user_id)
    self.name:str = "Journal Entries"

  def generate(self, t:List[str]) -> Optional[List[List[str]]]:
    # Generate prompt
    prompt = generate_prompt({
      "date":str(datetime.strptime(t[1], "%Y-%m-%d").date()),
      "amount":str(float(t[2])),
      "detail":str(t[6]),
      "payment_channel":str(t[7]),
      "merchant_name":str(t[8]),
      "pending":str(t[10]),
    })
    # Get gemini response
    try: response = gemini_response(prompt)
    except Exception as e:
      log.error(f"Error getting gemini response: {e}")
      return None
    # Sanitize gemini response
    r = sanitize_gemini_response(response)
    # Use sanitized response to create journal entry list
    # log.info(f"Sanitized Response:\n{r}")
    # TODO: Handle multiple debit and credit amount
    return [
      [str(r.date), r.description, r.debit[0].name, r.debit[0].account_id, r.debit[0].amount, ""],
      ["", "", r.credit[0].name, r.credit[0].account_id, "", r.credit[0].amount]
    ]

  def append(self, transaction) -> bool:
    """
    Append a row to the sheet
    """
    try:
      self.s_service.spreadsheets().values().append(
        spreadsheetId=self.spreadsheet_id,
        range=self.name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': [transaction]}
      ).execute()
    except Exception as e:
      log.error(f"Error appending to sheet: {e}")
      return False
    return True
