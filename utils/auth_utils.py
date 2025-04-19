import os
from google_auth_oauthlib.flow import Flow
import requests
from typing import Optional, List


TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
TOKEN_REFRESH_URL = "https://oauth2.googleapis.com/token"

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
  config = Flow.from_client_config(
    client_config,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URL
  )
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
  config = Flow.from_client_config(
    client_config,
    scopes=scopes,
    redirect_uri=REDIRECT_URL
  )
  return config


def verify_access_token(access_token: str) -> bool:
  """
    Verify google access token.
  """
  try:
    # Verify access token
    response = requests.get(
      TOKEN_INFO_URL,
      params={'access_token': access_token},
      timeout=10  # Add a timeout
    )
  except Exception as e:
      print(f"Error verifying access token: {e}")
      return False
  if response.status_code != 200:
    print("")
    return False
  return True


def refresh_access_token(access_token: str, refresh_token: str) -> tuple[Optional[str], bool]:
  """
    Refresh google access token.
  """
  CLIENT_ID = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
  CLIENT_SECRET = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
  payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token'
  }
  try:
    response = requests.post(
      TOKEN_REFRESH_URL,
      data=payload,
      timeout=15
    )

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
