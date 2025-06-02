from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from redis import Redis
from typing import Optional, Tuple, Any, List
import os
from utils.constants import TOKEN_URL
from utils.logger import log
from utils.types import JournalEntry
from utils.context import DEBUG
from datetime import datetime
from prompt.journal_entry import generate_prompt
from agents.gemini import gemini_response, sanitize_gemini_response
from helpers.parse_gs import google_script
from helpers.perf import perf


FONT_FAMILY = "Roboto"


class GoogleSheet:
  def __init__(self, redis:Redis,  user_id:str, name:Optional[str]=None, init:bool=False) -> None:
    self._user_id = user_id
    self._name = name
    self._redis = redis

    self.sheet_service, self.drive_service, self.script_service = self._create_service()
    if self.sheet_service is None or self.drive_service is None or self.script_service is None:
      raise ValueError("Error creating a service")

    if init:
      parent_id = self._create_folder("thinkledger")
      if parent_id is None: raise ValueError("Error creating thinkledger folder")

      general_ledger_id = self._create_folder("general_ledger", parent_id)
      if general_ledger_id is None: raise ValueError("Error creating general ledger folder")

      file_name = f"ledger_{datetime.now().year}"
      spreadsheet_id = self._create_spreadsheet(file_name, general_ledger_id)
      if spreadsheet_id is None: raise ValueError("Error creating spreadsheet file")

      script_is_created = self._create_google_script(general_ledger_id, spreadsheet_id)
      if script_is_created is None: raise ValueError("Error creating google script")

      self.spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

  def _create_service(self) -> Tuple[Any, Any, Any]:
    """
    Create a google sheet service and a google drive service; returns None if failed
    """
    client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
    if client_id is None: raise ValueError("Client ID is not found")
    if client_secret is None: raise ValueError("Client secret is not set")

    # Verify access token; and if expired, use refresh token to get new access token
    try:
      access_token = self._redis.get(f"service_access_token:{self._user_id}")
      refresh_token = self._redis.get(f"service_refresh_token:{self._user_id}")
    except Exception as e:
      log.error(f"Error getting access token and refresh token: {e}")
      return None, None, None

    if access_token is None:
      log.error("Service access token not found in redis")
      return None, None, None

    credentials:Credentials = Credentials(
      token=str(access_token),
      token_uri=TOKEN_URL,
      refresh_token=str(refresh_token),
      client_id=client_id,
      client_secret=client_secret,
    )

    try:
      sheets_service = build("sheets", "v4", credentials=credentials)
      drive_service = build("drive", "v3", credentials=credentials)
      script_service = build('script', 'v1', credentials=credentials)
      return sheets_service, drive_service, script_service
    except Exception as e:
      log.error(f"Error creating Google Sheets service or Google Drive service: {e}")
      return None, None, None

  def _create_folder(self, name:str, parent_id:str="root") -> Optional[str]:
    """
    Create a folder in the user's google drive. The parent_id specifies the parent folder id; if it
    is "root", the folder will be created in the root directory.
    """
    try: # Check if folder exists
      query = f"""
      name='{name}' and mimeType='application/vnd.google-apps.folder' and
      '{parent_id}' in parents and trashed=false
      """
      results = self.drive_service.files().list(q=query).execute()
      files = results.get('files', [])
      if files: return str(files[0].get("id"))
    except Exception as e:
      log.error(f"Error checking if {name} folder exist: {e}")
      return None

    metadata = {
      'name': name,
      'mimeType': 'application/vnd.google-apps.folder',
      "parents": [parent_id]
    }

    try: # Create folder if it doesn't exist
      folder = self.drive_service.files().create(body=metadata, fields='id').execute()
      if DEBUG >= 1: log.info(f"{name} folder created")
      return str(folder.get('id'))
    except Exception as e:
      log.error("Error creating folder: ", e)
      return None

  def _create_spreadsheet(self, file_name:str, folder_id:str) -> Optional[str]:
    """
    Create a spreadsheet file in a folder
    NOTE:
    if spreadsheet file name changes it means the year has changed, write a function that pulls in
    all the relevant data from the pervious year.
    """
    try: # Check if spreadsheet exists
      query = f"""
      name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'
      and '{folder_id}' in parents and trashed=false
      """
      results = self.drive_service.files().list(q=query).execute()
      files = results.get('files', [])
      if files: return str(files[0].get('id'))
    except Exception as e:
      log.error(f'Error checking if spreadsheet file exists: {e}')
      return None

    # Create new spreadsheet
    body = {
      "properties": {
        "title": file_name,
        "defaultFormat": {
          "textFormat": { "fontFamily": FONT_FAMILY, "fontSize": 11, }
        },
      },
    }

    # Create spreadsheet file
    try: spreadsheet = self.sheet_service.spreadsheets().create(body=body).execute()
    except Exception as e:
      log.error(f"Error creating spreadsheet file: {e}")
      return None

    try: # Move to correct folder
      spreadsheet_id = spreadsheet.get('spreadsheetId')
      self.drive_service.files().update(
        fileId=spreadsheet_id,
        addParents=folder_id,
        removeParents='root',
        fields='id, parents'
      ).execute()
      if DEBUG >= 1: log.info("Spreadsheet file created")
      return str(spreadsheet_id)
    except Exception as e:
      log.error(f'Error moving spreadsheet to the right folder: {e}')
      return None

  def _create_google_script(self, folder_id:str, spreadsheet_id:str) -> Optional[bool]:
    file_name = "google_script"
    try: # Check if app script exists
      query = f"""
      name='{file_name}' and mimeType='application/vnd.google-apps.script'
      and '{folder_id}' in parents and trashed=false
      """
      results = self.drive_service.files().list(q=query).execute()
      files = results.get('files', [])
      if files: return True
    except Exception as e:
      log.error(f"Error occurred while checking if app script file exists: {e}")
      return None

    try: # Create the script project
      script_project = self.script_service.projects().create(body={
        "title": file_name,
        "parentId": spreadsheet_id  # Binds to the spreadsheet
      }).execute()
      if DEBUG >= 1: log.info("App script file created")
    except Exception as e:
      log.error(f"Error creating app script project: {e}")
      return None

    manifest = """
    {
      "timeZone": "America/New_York",
      "dependencies": {},
      "exceptionLogging": "STACKDRIVER",
      "runtimeVersion": "V8",
      "oauthScopes": [
        "https://www.googleapis.com/auth/spreadsheets.currentonly",
        "https://www.googleapis.com/auth/script.external_request"
      ]
    }
    """
    code_gs = google_script(self._user_id, self._redis)
    try: # Update app script file
      self.script_service.projects().updateContent(
        scriptId=script_project.get("scriptId"),
        body={
          'files': [
            {'name': file_name, 'type': 'SERVER_JS', 'source': code_gs},
            { 'name': 'appsscript', 'type': 'JSON', 'source': manifest }
          ]
        }
      ).execute()
      if DEBUG >= 1: log.info("Google script file updated")
    except Exception as e:
      log.error(f"Error updating app script project: {e}")
      return None
    return True

  def append(self, spreadsheet_id:str, values:List[List[str]]) -> bool:
    """
    Append values to a sheet line by line
    """
    try:
      self.sheet_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=self._name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': values}
      ).execute()
      return True
    except Exception as e:
      log.error(f"Error appending line to {self._name} sheet: {e}")
      return False


class TransactionSheet(GoogleSheet):
  def __init__(self, redis:Redis, user_id:str) -> None:
    name:str = "Transactions"
    super().__init__(redis, user_id, name)


class JournalEntrySheet(GoogleSheet):
  def __init__(self, redis:Redis, user_id:str) -> None:
    name:str = "Journal Entries"
    super().__init__(redis, user_id, name)

  @perf
  def generate(self, t:List[str]) -> Optional[List[List[str]]]:
    # Generate prompt
    prompt = generate_prompt({
      "date": t[1],
      "amount": t[2],
      "detail": t[6],
      "payment_channel": t[7],
      "merchant_name": t[8],
      "pending": t[10],
    })
    # Get gemini response
    try: response = gemini_response(prompt)
    except Exception as e:
      log.error(f"Error getting gemini response: {e}")
      return None
    # Sanitize gemini response
    try: sanitized_response = sanitize_gemini_response(response)
    except Exception as e:
      log.error(f"Error sanitizing gemini response: {e}")
      return None

    if DEBUG >= 2: log.info(f"sanitized_response: {sanitized_response}")

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
      for c in r.credit: m_list.append(["", "", c.name, c.account_id, "", c.amount])
      return m_list
    return helper(sanitized_response)
