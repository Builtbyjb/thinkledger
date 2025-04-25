import os
from google_auth_oauthlib.flow import Flow # type: ignore
import requests
from typing import Optional, List
from database.redis.redis import gen_redis
from utils.constants import TOKEN_INFO_URL, TOKEN_URL


def sign_in_auth_config() -> Flow:
  """
    Google user authentication oauth configuration
  """
  SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
  ]
  CLIENT_ID = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
  CLIENT_SECRET = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
  REDIRECT_URL = os.getenv("GOOGLE_SIGNIN_REDIRECT_URL")
  # SERVER_URL = os.getenv("SERVER_URL")

  client_config = {
    "web": {
      "client_id": CLIENT_ID,
      "client_secret": CLIENT_SECRET,
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "redirect_uris": [REDIRECT_URL],
    }
  }
  config = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URL)
  return config

def service_auth_config(scopes: List[str]) -> Flow:
  """
    Takes in a list of user selected scopes
    Create google service access grant oauth configuration
  """
  CLIENT_ID = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
  CLIENT_SECRET = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
  REDIRECT_URL = os.getenv("GOOGLE_SERVICE_REDIRECT_URL")
  # SERVER_URL = os.getenv("SERVER_URL")

  client_config = {
    "web": {
      "client_id": CLIENT_ID,
      "client_secret": CLIENT_SECRET,
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "redirect_uris": [REDIRECT_URL],
    }
  }
  config = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=REDIRECT_URL)
  return config

def verify_access_token(access_token: str) -> bool:
  """
    Verify google access token.
  """
  try: response = requests.get(TOKEN_INFO_URL, params={'access_token': access_token}, timeout=10)
  except Exception as e:
      print(f"Error verifying access token: {e}")
      return False
  if response.status_code != 200:
    print("Error verifying access token")
    return False
  return True

def refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> tuple[Optional[str], bool]:
  """
    Refresh google access token.
  """
  payload = {
    'client_id':client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token'
  }

  try:
    response = requests.post(TOKEN_URL, data=payload, timeout=15)
    if response.status_code == 200:
      token_json = response.json()
      new_access_token = str(token_json["access_token"])
      return new_access_token, True
    else:
      print(f"Token Refresh Error: {response.status_code} : {response.text}")
      return None, False
  except requests.exceptions.Timeout:
    print("Token Refresh Error: Request timed out.")
    return None, False

def auth_session(session_id: str) -> bool:
  """
    Authenticates a user by verifying their access token and refreshing it if necessary.
  """
  redis = gen_redis()
  if redis is None: return False

  try:
    user_id = str(redis.get(session_id))
    access_token  = str(redis.get(f"access_token:{user_id}"))
  except Exception as e:
    print(f"Error fetching user data or access token: {e}")
    return False

  # Verify access token
  if not verify_access_token(access_token):
    # If access token verification fails, try refreshing the token
    try: refresh_token = str(redis.get(f"refresh_token:{user_id}"))
    except Exception as e:
      print(f"Error fetching refresh token: {e}")
      return False

    if refresh_token is None: return False

    client_id = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")

    if client_id is None: return False
    if client_secret is None: return False

    new_access_token, is_refreshed = refresh_access_token(refresh_token, client_id, client_secret)
    if not is_refreshed or new_access_token is None: return False

    try: redis.set(f"access_token:{user_id}", new_access_token)
    except Exception as e:
      print(f"Error setting new access token: {e}")
      return False

  return True
