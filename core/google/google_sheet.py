from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from database.redis.redis import gen_redis
from typing import Optional, Tuple, Any, List, Dict
import os, time
from utils.constants import TOKEN_URL
from utils.logger import log
from utils.types import JournalEntry
from datetime import datetime
from prompt.journal_entry import generate_prompt
from agents.gemini import gemini_response, sanitize_gemini_response
from helpers.parse_app_script import get_app_script


FONT_FAMILY = "Roboto"


class GoogleSheet:
  def __init__(self, user_id:str, name:Optional[str]=None, init:bool=False):
    self.user_id = user_id
    self.name = name

    self.sheet_service, self.drive_service, self.script_service = self.create_service()
    if self.sheet_service is None or self.drive_service is None or self.script_service is None:
      raise ValueError("Error creating a service")

    if init:
      parent_id = self.create_folder("thinkledger")
      if parent_id is None: raise ValueError("Error creating thinkledger folder")

      general_ledger_id = self.create_folder("general_ledger", parent_id)
      if general_ledger_id is None: raise ValueError("Error creating general ledger folder")

      file_name = f"ledger_{datetime.now().year}"
      spreadsheet_id = self.create_spreadsheet(file_name, general_ledger_id)
      if spreadsheet_id is None: raise ValueError("Error creating spreadsheet file")
      self.spreadsheet_id = spreadsheet_id

      self.create_app_script(general_ledger_id)

  def create_service(self) -> Tuple[Any, Any, Any]:
    """
    Create a google sheet service and a google drive service; returns None if failed
    """
    redis = gen_redis()
    if redis is None: return None, None, None

    client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
    if client_id is None: raise ValueError("Client ID is not found")
    if client_secret is None: raise ValueError("Client secret is not set")

    # Verify access token; and if expired, use refresh token to get new access token
    try:
      access_token = redis.get(f"service_access_token:{self.user_id}")
      refresh_token = redis.get(f"service_refresh_token:{self.user_id}")
    except Exception as e:
      log.error(f"Error getting access token and refresh token: {e}")
      return None, None, None

    if access_token is None:
      log.error("Service access token not found in redis")
      return None, None, None

    credentials = Credentials(
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

  def create_folder(self, name:str, parent_id:str="root") -> Optional[str]:
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
      log.info(f"{name} folder created")
      return str(folder.get('id'))
    except Exception as e:
      log.error("Error creating folder: ", e)
      return None

  def create_spreadsheet(self, file_name:str, folder_id:str) -> Optional[str]:
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
    # TODO: Change default spreadsheet name, set default font size
    body = {
      "properties": {
        "title": file_name,
        "spreadsheetTheme": {
          "primaryFontFamily": FONT_FAMILY,
          "themeColors": [
            # {"colorType": "THEME_COLOR_TYPE_UNSPECIFIED", "color": {}},
            {
              "colorType": "TEXT",
              "color": { "rgbColor": {"red":0.0, "green":0.0, "blue": 0.0} }, # Black
            },
            {
              "colorType": "BACKGROUND",
              "color": { "rgbColor": {"red":1.0, "green":1.0, "blue":1.0}}, # White
            },
            { # A shade of blue
              "colorType": "ACCENT1",
              "color": { "rgbColor": {"red":60/255, "green":120/255, "blue":216/255}},
            },
            { # A shade of orange/red
              "colorType": "ACCENT2",
              "color": { "rgbColor": {"red":221/255, "green":126/255, "blue":107/255}},
            },
            { # A shade of purple
              "colorType": "ACCENT3",
              "color": { "rgbColor": {"red":152/255, "green":118/255, "blue":170/255} },
            },
            { # A shade of teal
              "colorType": "ACCENT4",
              "color": { "rgbColor": {"red":109/255, "green":194/255, "blue":202/255} },
            },
            { # A shade of yellow
              "colorType": "ACCENT5",
              "color": { "rgbColor": {"red":241/255, "green":194/255, "blue":50/255} },
            },
            { # A shade of green
              "colorType": "ACCENT6",
              "color": { "rgbColor": {"red":127/255, "green":199/255, "blue":132/255} },
            },
            { # Standard link blue
              "colorType": "LINK",
              "color": { "rgbColor": {"red":17/255, "green":85/255, "blue":204/255} }
            },
          ]
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
      # print(spreadsheet_id)
      log.info("Spreadsheet file created")
      return str(spreadsheet_id)
    except Exception as e:
      log.error(f'Error moving spreadsheet to the right folder: {e}')
      return None

  def create_app_script(self, folder_id:str) -> None:
    file_name = "app_script"
    try: # Check if app script exists
      query = f"""
      name='{file_name}' and mimeType='application/vnd.google-apps.script'
      and '{folder_id}' in parents and trashed=false
      """
      results = self.drive_service.files().list(q=query).execute()
      files = results.get('files', [])
      if files: return None
    except Exception as e:
      log.error(f"Error occurred while checking if app script file exists: {e}")
      return None

    try: # Create the script project
      script_project = self.script_service.projects().create(body={
        "title": "app_script",
        "parentId": self.spreadsheet_id  # Binds to the spreadsheet
      }).execute()
      log.info("App script file created")
    except Exception as e:
      log.error(f"Error creating app script project: {e}")
      return None

    manifest = """
    {
      "timeZone": "America/New_York",
      "dependencies": {},
      "exceptionLogging": "STACKDRIVER",
      "runtimeVersion": "V8",
      "oauthScopes": ["https://www.googleapis.com/auth/spreadsheets.currentonly"]
    }
    """

    # Get google app script and manifest file
    app_script = get_app_script()

    try: # Update app script file
      self.script_service.projects().updateContent(
        scriptId=script_project.get("scriptId"),
        body={
          'files': [
            {'name': file_name, 'type': 'SERVER_JS', 'source': app_script},
            { 'name': 'appsscript', 'type': 'JSON', 'source': manifest }
          ]
        }
      ).execute()
      log.info("App script file updated")
    except Exception as e:
      log.error(f"Error updating app script project: {e}")
      return None
    return None

  def create_sheet(self, idx:int, name:str, header:List[str], h_range:str) -> Optional[str]:
    """
    Create a sheet in the spreadsheet file
    """
    try: # Get all sheets in the spreadsheet
      metadata = self.sheet_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
      sheets = metadata.get('sheets', [])

      # Check if sheet already exists
      # sheet_exists = any(sheet.get('properties', {}).get('title') == name for sheet in sheets)
      for s in sheets:
        if s.get("properties", {}).get("title") == name:
          return str(s.get("properties", {}).get("sheetId"))

      def generate_column(header:List[str]) -> List[Dict[str,Any]]:
        """
        Generate table columns for header list
        """
        column_list = {
          "ID": "TEXT",
          "Date": "DATE_TIME",
          "Amount": "CURRENCY",
          "Institution": "TEXT",
          "Institution Account Name": "TEXT",
          "Institution Account Type": "TEXT",
          "Category": "TEXT",
          "Payment Channel": "TEXT",
          "Merchant Name": "TEXT",
          "Currency": "TEXT",
          "Pending": "BOOLEAN",
          "Authorized Date": "DATE_TIME"
        }

        l:List[Dict[str,Any]] = []
        for i, v in enumerate(header):
          l.append({
            "columnIndex": i,
            "columnName": v,
            "columnType": column_list[v],
            # "dataValidationRule": {}
          })
        return l

      if header: # Create a table heading if a header is provided
        table = {
          "tableId": "table",
          "name": "name",
          "range": {
            'sheetId': idx,
            'startRowIndex': 6,
            'endRowIndex': 7,
            'startColumnIndex': 0,
            'endColumnIndex': len(header)
          },
          "rowsProperties": {
            "headerColorStyle": {
              "rgba": { "red":0.5, "green": 0.5, "blue": 0.5 } # , "alpha": number }
            }
          },
          "columnProperties": [generate_column(header)]
        }
      else: table = {}

      # Create a new sheet
      body = {
        "requests": [{
          "addSheet": {
            "properties": { "title": name, "sheetId": idx, "index": idx },
            "data": [
              { # Add main header
                "startRow": 0,
                "startColumn": 0,
                "rowData": [{"values":{
                  "userEnteredValue": {"stringValue": name},
                  "userEnteredFormat": {
                    "backgroundColorStyle": { "red": 0.1, "green": 0.1, "blue": 0.1 },
                    "textFormat": {
                      "foregroundColor": { "red": 1.0, "green": 1.0, "blue": 1.0 },
                      'fontSize': 14,
                      'bold': True,
                      'fontFamily': FONT_FAMILY
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                  },
                }}]
              },
            ],
            "tables":[table], # Add table heading
            "merges": [
              { # Merge main header cells
                "sheetId": idx,
                "startRowIndex": 0,
                "endRowIndex": 4,
                "startColumnIndex": 0,
                "endColumnIndex": 6,
              }
            ]
          }
        }]
      }

      response = self.sheet_service.spreadsheets() \
        .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
      log.info(f"Created new {name} sheet")

      # Get the new sheet ID from response
      sheet_id = response.get('replies', [])[0].get('addSheet', {}).get('properties', {}) \
        .get('sheetId')
      if sheet_id is None:
        log.error("Failed to get sheet ID from response")
        return None
      print(sheet_id)
      return str(sheet_id)
    except Exception as e:
      log.error(f"Error creating {name} sheet: {e}")
      return None

  def setup_transaction(self) -> str:
    name:str = "Transactions"
    header:List[str] = [
      'ID', 'Date', 'Amount', 'Institution', 'Institution Account Name', 'Institution Account Type',
      'Category', 'Payment Channel', 'Merchant Name', 'Currency', 'Pending', 'Authorized Date']
    h_range:str = "Transactions!A4:L4"
    idx:int = 3
    sheet_id = self.create_sheet(idx, name, header, h_range)
    if sheet_id is None: raise ValueError("Error creating transaction sheet")
    return sheet_id

  def setup_journal_entry(self) -> str:
    name:str = "Journal Entries"
    header:List[str] = ["Date", "Description", "Account Name", "Account ID", "Debit", "Credit"]
    h_range:str = "Journal Entries!A4:F4"
    idx:int = 4
    sheet_id = self.create_sheet(idx, name, header, h_range)
    if sheet_id is None: raise ValueError("Error creating journal entry sheet")
    return sheet_id

  def setup_t_account(self) -> None:
    # name:str = "T Accounts"
    return None

  def setup_trial_bal(self) -> None:
    return None

  def setup_bal_sheet(self) -> None:
    return None

  def append_line(self, values:List[List[str]]) -> bool:
    """
    Append values to a sheet line by line
    """
    try:
      self.sheet_service.spreadsheets().values().append(
        spreadsheetId=self.spreadsheet_id,
        range=self.name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': values}
      ).execute()
      # TODO: Add styling
      return True
    except Exception as e:
      log.error(f"Error appending line to {self.name} sheet: {e}")
      return False

  def append_char(self, values:List[List[str]]) -> bool:
    """
    Append values to a sheet character by character
    """
    try:
      # Get last row number
      result = self.sheet_service.spreadsheets().values().get(
        spreadsheetId=self.spreadsheet_id,
        range=f"{self.name}!A:A"
      ).execute()
      next_row = len(result.get('values', [])) + 1

      for col_idx, value in enumerate(values):
        str_value = str(value)
        # Stream each character of the value
        for i in range(len(str_value) + 1):
          partial_value = str_value[:i]
          request = {
            'updateCells': {
              'rows': [{
                'values': [{
                  'userEnteredValue': {'stringValue': partial_value },
                  'userEnteredFormat': {
                    'textFormat': {
                      'fontFamily': 'Arial',
                      'fontSize': 11,
                      'foregroundColor': { 'red': 0.1, 'green': 0.1, 'blue': 0.1 }
                    },
                    'borders': {
                      'bottom': {
                        'style': 'SOLID',
                        'width': 1,
                        'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
                      },
                      'right': {
                        'style': 'SOLID',
                        'width': 1,
                        'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
                      }
                    },
                    'horizontalAlignment': 'LEFT' if col_idx in [1, 3, 4, 6, 8] else 'RIGHT',
                    'verticalAlignment': 'MIDDLE',
                    # Alternate row colors
                    'backgroundColor': {
                      'red': 1.0 if next_row % 2 == 0 else 0.95,
                      'green': 1.0 if next_row % 2 == 0 else 0.95,
                      'blue': 1.0 if next_row % 2 == 0 else 0.95
                    }
                  }
                }]
              }],
              'fields': """userEnteredValue,userEnteredFormat(backgroundColor,textFormat,borders,
                horizontalAlignment,verticalAlignment)""",
              'range': {
                # 'sheetId': self.trans_sheet_id,
                'startRowIndex': next_row - 1,
                'endRowIndex': next_row,
                'startColumnIndex': col_idx,
                'endColumnIndex': col_idx + 1
              }
            }
          }

          # Execute update for each character
          self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={'requests': [request]}
          ).execute()

          # Add typing delay (adjust for desired speed)
          time.sleep(0.05)  # 50ms between characters

        # Add delay between cells
        time.sleep(0.2)  # 200ms between cells
      return True
    except Exception as e:
      log.error(f"Error appending to sheet: {e}")
      return False


class TransactionSheet(GoogleSheet):
  def __init__(self, user_id:str):
    name:str = "Transactions"
    super().__init__(user_id, name)


class JournalEntrySheet(GoogleSheet):
  def __init__(self, user_id:str):
    name:str = "Journal Entries"
    super().__init__(user_id, name)

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
    try: r = sanitize_gemini_response(response)
    except Exception:
      log.error("Error sanitizing gemini response")
      return None
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
      for c in r.credit: m_list.append(["", "", c.name, c.account_id, "", c.amount])
      return m_list

    return helper(r)
