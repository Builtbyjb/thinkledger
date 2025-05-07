from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from database.redis.redis import gen_redis
from typing import Optional, Tuple
import os
from utils.constants import TOKEN_URL
from utils.logger import log


def create_service(user_id: str) -> Tuple[Optional[object], Optional[object]]:
  """
  Create a google sheet service and a google drive service; returns None if failed
  """
  redis = gen_redis()
  if redis is None: return None, None

  client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
  client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")

  # Verify access token; and if expired, use refresh token to get new access token
  access_token = redis.get(f"service_access_token:{user_id}")
  if access_token is None:
    log.error("Service access token not found in redis")
    return None, None
  assert isinstance(access_token, str), "Access token is not a string"

  refresh_token = redis.get(f"service_refresh_token:{user_id}")

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
    # Add more detailed error information
    import traceback
    log.error(f"Detailed error: {traceback.format_exc()}")
    return None, None
  return sheets_service, drive_service


def create_folder(drive_service, name: str, user_id: str, parent_id: str="root") -> Optional[str]:
  """
  Create a folder in the user's google drive.
  The parent_id specifies the parent folder id; if it is "root", the folder will be created
  in the root directory.
  """
  redis = gen_redis()
  if redis is None: return None

  try:
    # Check if parent folder exists
    query = f"""
    name='{name}' and mimeType='application/vnd.google-apps.folder' and
    '{parent_id}' in parents and trashed=false
    """
    results = drive_service.files().list(q=query).execute()
    items = results.get('files', [])

    # Create parent folder if it doesn't exist
    if not items:
      metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        "parents": [parent_id]
      }
      folder = drive_service.files().create(body=metadata, fields='id').execute()
      folder_id = folder.get('id')
    else: folder_id = items[0].get('id')
  except Exception as e:
    log.error("Error creating folder: ", e)
    return None

  # Store the folder id in redis
  try: redis.set(f"{name}:{user_id}", folder_id)
  except Exception as e:
    log.error("Error storing folder id in redis: ", e)
    return None
  return folder_id


def create_spreadsheet(
    d_service, s_service, name: str, folder_id: str, user_id: str
    ) -> Optional[str]:
  """
  Create a spreadsheet file in a folder
  """
  redis = gen_redis()
  if redis is None: return None

  try:
    # Check if spreadsheet exists
    query = f"""
    name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'
    and '{folder_id}' in parents and trashed=false
    """
    results = d_service.files().list(q=query).execute()
    files = results.get('files', [])

    if files: return files[0].get('id')

    # Create new spreadsheet
    spreadsheet_body = {'properties': {'title': name}}
    spreadsheet = s_service.spreadsheets().create(body=spreadsheet_body).execute()

    # Move to correct folder
    spreadsheet_id = spreadsheet.get('spreadsheetId')
    d_service.files().update(
      fileId=spreadsheet_id,
      addParents=folder_id,
      removeParents='root',
      fields='id, parents'
    ).execute()
  except Exception as e:
    log.error(f'Google Sheets API error: {e}')
    return None

  # Store the spreadsheet id in redis
  try: redis.set(f"{name}:{user_id}", spreadsheet_id)
  except Exception as e:
    log.error("Error storing spreadsheet id in redis: ", e)
    return None
  return spreadsheet_id


def create_transaction_sheet(s_service, spreadsheet_id: str) -> None:
  """
  Create a sheet in the spreadsheet file
  """
  # First, check if the Transactions sheet already exists
  try:
    # Get spreadsheet information to check for existing sheets
    spreadsheet = s_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    # Check if Transactions sheet already exists
    sheet_exists = False
    for sheet in spreadsheet.get('sheets', []):
      if sheet.get('properties', {}).get('title') == 'Transactions':
        sheet_exists = True
        break

    # If the sheet doesn't exist, create it
    if not sheet_exists:
      # Create a new Transactions sheet
      body = {
        'requests': [{
          'addSheet': {
            'properties': {
              'title': 'Transactions'
            }
          }
        }]
      }
      s_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
      log.info("Created new Transactions sheet")

    # Add headers
    headers = [
      [
        'ID', 'Date', 'Amount', 'Institution', 'Institution Account Name',
        'Institution Account Type', 'Category', 'Payment Channel', 'Merchant Name', 'Currency',
        'Pending', 'Authorized Date'
      ]
    ]

    # Update the sheet with headers
    s_service.spreadsheets().values().update(
      spreadsheetId=spreadsheet_id,
      range='Transactions!A1:L1',
      valueInputOption='RAW',
      body={'values': headers}
    ).execute()
    log.info("Added headers to Transactions sheet")

  except Exception as e:
    log.error(f"Error creating transaction sheet: {e}")
    import traceback
    log.error(f"Detailed error: {traceback.format_exc()}")

  return None


def append_to_sheet(transaction, s_service, spreadsheet_id: str, name) -> bool:
  """
  Append a row to the sheet
  """
  try:
    s_service.spreadsheets().values().append(
      spreadsheetId=spreadsheet_id,
      range=name,
      valueInputOption='USER_ENTERED',
      insertDataOption='INSERT_ROWS',
      body={'values': [transaction]}
    ).execute()
  except Exception as e:
    log.error(f"Error appending to sheet: {e}")
    return False
  return True
