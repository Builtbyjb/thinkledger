import os
from google_auth_oauthlib.flow import Flow # type: ignore
import requests
from typing import Optional, List
from database.redis.redis import gen_redis
from utils.constants import TOKEN_INFO_URL, TOKEN_URL
from utils.logger import log


def sign_in_auth_config() -> Flow:
  """
    Google user authentication oauth configuration
  """
  scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
  ]
  client_id = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
  client_secret = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
  server_url = os.getenv("SERVER_URL")
  if client_id is None: raise ValueError("Google client id is not found")
  if client_secret is None: raise ValueError ("Google signin client secret not found")
  if server_url is None: raise ValueError("Google server url is not set")

  redirect_url = f"{server_url}/google/callback/sign-in"

  client_config = {
    "web": {
      "client_id": client_id,
      "client_secret": client_secret,
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "redirect_uris": [redirect_url],
    }
  }
  return Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_url)


def service_auth_config(scopes: List[str]) -> Flow:
  """
    Takes in a list of user selected scopes
    Create google service access grant oauth configuration
  """
  client_id = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
  client_secret = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
  server_url = os.getenv("SERVER_URL")
  if client_id is None: raise ValueError("Google service client id not found")
  if client_secret is None: raise ValueError("Google service client secret not found")
  if server_url is None: raise ValueError("Google server url not found")
  if len(scopes) > 0: raise Exception("Scopes list can not be empty")

  redirect_url = f"{server_url}/google/callback/services"

  client_config = {
    "web": {
      "client_id": client_id,
      "client_secret": client_secret,
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "redirect_uris": [redirect_url],
    }
  }
  return Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_url)


def verify_access_token(access_token:str) -> bool:
  """
    Verify google access token.
  """
  try: response = requests.get(TOKEN_INFO_URL, params={'access_token': access_token}, timeout=10)
  except Exception as e:
      log.error(f"Error verifying access token: {e}")
      return False

  if response.status_code != 200:
    log.error("Error verifying access token")
    return False
  return True


def refresh_access_token(refresh_token:str, client_id:str,client_secret:str) -> Optional[str]:
  """
    Refresh google access token.
  """
  payload = {
    'client_id':client_id,
    'client_secret':client_secret,
    'refresh_token':refresh_token,
    'grant_type':'refresh_token'
  }

  try:
    response = requests.post(TOKEN_URL, data=payload, timeout=15)
    if response.status_code == 200:
      token_json = response.json()
      new_access_token = str(token_json["access_token"])
      return new_access_token

    log.error(f"Token Refresh Error: {response.status_code} : {response.text}")
    return None
  except requests.exceptions.Timeout:
    log.error("Token Refresh Error: Request timed out.")
    return None


def auth_session(session_id: str) -> bool:
  """
    Authenticates a user by verifying their access token and refreshing it if necessary.
  """
  redis = gen_redis()
  if redis is None: return False

  try:
    user_id = redis.get(session_id)
    access_token = redis.get(f"access_token:{user_id}")
  except Exception as e:
    log.error(f"Error fetching user data or access token: {e}")
    return False

  if user_id is None: 
    log.error("User not found")
    return False

  if access_token is None: 
    log.error("Not access token")
    return False

  # Verify access token
  if not verify_access_token(str(access_token)):
    # If access token verification fails, try refreshing the token
    try: refresh_token = redis.get(f"refresh_token:{user_id}")
    except Exception as e:
      log.error(f"Error fetching refresh token: {e}")
      return False

    if refresh_token is None:
      log.error("No refresh token found")
      return False

    client_id = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
    if client_id is None: raise ValueError("Google signin client id not found")
    if client_secret is None: raise ValueError("Google signin client secret not found")

    new_access_token = refresh_access_token(str(refresh_token), client_id, client_secret)
    if new_access_token is None:
      log.error("Error refreshing access token")
      return False

    try: redis.set(f"access_token:{user_id}", new_access_token)
    except Exception as e:
      log.error(f"Error setting new access token: {e}")
      return False

  return True
