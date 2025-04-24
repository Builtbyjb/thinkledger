from googleapiclient.discovery import build # type: ignore
from google.oauth2.credentials import Credentials
from database.redis.redis import gen_redis
from typing import Optional, Tuple
import os
from utils.constants import TOKEN_REFRESH_URL

CLIENT_ID = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")

def create_google_service(user_id: str) -> Tuple[Optional[object], Optional[object]]:
  """
  Create a google sheet service and a google drive service; returns None if failed
  """
  redis = gen_redis()
  if redis is None: return None, None

  # Verify access token; and if expired, use refresh token to get new access token
  access_token = redis.get(f"access_token:{user_id}")
  if access_token is None:
    print("Access token not found in redis")
    return None, None

  refresh_token = redis.get(f"refresh_token:{user_id}") # It is fine if it is None

  credentials = Credentials(
    token=access_token,
    token_uri=TOKEN_REFRESH_URL,
    refresh_token=refresh_token,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
  ) 
  
  try: 
    sheets_service = build("sheets", "v4", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
  except Exception as e:
    print("Error creating Google Sheets service or Google Drive service: ", e)
    return None, None
  return sheets_service, drive_service
