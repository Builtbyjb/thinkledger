from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from database.redis.redis import gen_redis
from typing import Optional, Tuple, Any, List
import os
from dataclasses import dataclass
from utils.constants import TOKEN_URL
from utils.logger import log
from utils.types import JournalEntry
from datetime import datetime
from prompt.journal_entry import generate_prompt
from agents.gemini import gemini_response, sanitize_gemini_response

# TODO: Ability to handle multiple business accounts.
# TODO: Ability to handle personal accounts .
# TODO: Handle transaction changes


@dataclass
class GoogleSheet:
  def __init__(self, user_id:str):
    self.user_id = user_id
    self.s_service, self.d_service = self.create_service()
    assert self.s_service is not None and self.d_service is not None
    parent_id = self.create_folder("thinkledger")
    assert isinstance(parent_id, str), "Error creating thinkledger folder"
    general_ledger_id = self.create_folder("general_ledger", parent_id)
    assert isinstance(general_ledger_id, str), "Error creating general ledger folder"
    file_name = f"ledger_{datetime.now().year}"
    spreadsheet_id = self.create_spreadsheet(file_name, general_ledger_id)
    assert isinstance(spreadsheet_id, str), "Error creating spreadsheet file"
    self.spreadsheet_id = spreadsheet_id
    self.trans_sheet_id = self.setup_transaction()
    self.journal_sheet_id = self.setup_journal_entry()
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
      return sheets_service, drive_service
    except Exception as e:
      log.error(f"Error creating Google Sheets service or Google Drive service: {e}")
      return None, None

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
      files = results.get('files', [])
      if files: return files[0].get("id")

      # Create folder if it doesn't exist
      metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        "parents": [parent_id]
      }
      folder = self.d_service.files().create(body=metadata, fields='id').execute()
      log.info("Folder created")
      return folder.get('id')
    except Exception as e:
      log.error("Error creating folder: ", e)
      return None

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
      log.info("Spreadsheet file created")
      return spreadsheet_id
    except Exception as e:
      log.error(f'Google Sheets API error: {e}')
      return None

  def create_sheet(self, name:str, header:List[str], h_range:str) -> Optional[str]:
    """
    Create a sheet in the spreadsheet file
    """
    try:
      # Get all sheets in the spreadsheet
      metadata = self.s_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
      sheets = metadata.get('sheets', [])

      # Check if sheet already exists
      # sheet_exists = any(sheet.get('properties', {}).get('title') == name for sheet in sheets)
      for s in sheets:
        if s.get("properties", {}).get("title") == name:
          return s.get("properties", {}).get("sheetId")

      # Create a new sheet
      body = {
        'requests': [{
          'addSheet': {
            'properties': { 'title': name }
          }
        }]
      }

      response = self.s_service.spreadsheets() \
        .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
      log.info(f"Created new {name} sheet")
       # Get the new sheet ID from response
      sheet_id = response.get('replies', [])[0].get('addSheet', {}).get('properties', {}) \
        .get('sheetId')
      if sheet_id is None:
        log.error("Failed to get sheet ID from response")
        return None

      # Update the sheet with headers
      self.s_service.spreadsheets().values().update(
        spreadsheetId=self.spreadsheet_id,
        range=h_range,
        valueInputOption='RAW',
        body={'values':[header]}
      ).execute()
      log.info(f"Added headers to {name} sheet")
      return str(sheet_id)
    except Exception as e:
      log.error(f"Error creating {name} sheet: {e}")
      return None

  def setup_transaction(self) -> str:
    name:str = "Transactions"
    header:List[str] = [
      'ID', 'Date', 'Amount', 'Institution', 'Institution Account Name', 'Institution Account Type',
      'Category', 'Payment Channel', 'Merchant Name', 'Currency', 'Pending', 'Authorized Date'
    ]
    h_range:str = "Transactions!A1:L1"
    sheet_id = self.create_sheet(name, header, h_range)
    assert sheet_id is not None
    return  sheet_id

  def setup_journal_entry(self) -> str:
    name:str = "Journal Entries"
    header:List[str] = ["Date", "Description", "Account Name", "Account ID", "Debit", "Credit"]
    h_range:str = "Journal Entries!A1:F1"
    sheet_id = self.create_sheet(name, header, h_range)
    assert sheet_id is not None
    return sheet_id

  def setup_t_account(self) -> None:
    return None

  def setup_trial_bal(self) -> None:
    return None

  def setup_bal_sheet(self) -> None:
    return None


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
      return True
    except Exception as e:
      log.error(f"Error appending to sheet: {e}")
      return False


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
    # print(f"Sanitized Response:\n{r}")

    def helper(r:JournalEntry) -> List[List[str]]:
      """
      Helps create a journal entry. Accounts for multiple debit and credit account values
      """
      m_list:List[List[str]] = []

      # Append first debit value, with date and description
      m_list.append([str(r.date), r.description, r.debit[0].name, r.debit[0].account_id,
                     r.debit[0].amount, ""])

      # Append debit values
      for i in range(len(r.debit)):
        if i == 0: continue
        m_list.append(["", "", r.debit[i].name, r.debit[i].account_id, r.debit[i].amount, ""])

      # Append credit values
      for c in r.credit:
        m_list.append(["", "", c.name, c.account_id, "", c.amount])

      return m_list

    return helper(r)

  def append(self, journal_entry:List[List[str]]) -> bool:
    """
    Append a row to the sheet
    """
    # TODO: Add styling
    try:
      self.s_service.spreadsheets().values().append(
        spreadsheetId=self.spreadsheet_id,
        range=self.name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': journal_entry}
      ).execute()
      return True
    except Exception as e:
      log.error(f"Error appending to sheet: {e}")
      return False
