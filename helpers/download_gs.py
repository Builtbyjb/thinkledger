#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from typing import Optional, Any


def get_service_flow() -> Optional[Flow]:
  scopes = ['https://www.googleapis.com/auth/script.projects.readonly']
  client_id = os.getenv("GOOGLE_SERVICE_DEV_CLIENT_ID")
  client_secret = os.getenv("GOOGLE_SERVICE_DEV_CLIENT_SECRET")
  if client_id is None: raise ValueError("client id not found")
  if client_secret is None: raise ValueError("Client secret not found")

  config = {
    "installed":{
      "client_id": client_id,
      "auth_uri":"https://accounts.google.com/o/oauth2/auth",
      "token_uri":"https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
      "client_secret": client_secret,
      "redirect_uris":["http://localhost"]
    }
  }

  try: flow = InstalledAppFlow.from_client_config(config, scopes)
  except Exception:
    print("Error getting google oauth flow")
    return None

  return flow


def download_gs(creds:Any) -> None:
  gs_filename = os.getenv("GOOGLE_SCRIPT_FILENAME")
  output_dir = os.getenv("GOOGLE_SCRIPT_OUTPUT_DIR")
  script_id = os.getenv("GOOGLE_SCRIPT_ID")
  if gs_filename is None: raise ValueError("Google filename not found")
  if output_dir is None: raise ValueError("Output dir not found")
  if script_id is None: raise ValueError("Google script id not found")

  try: script_service = build("script", "v1", credentials=creds)
  except Exception as e:
    sys.exit(f"Could not create script service: {e}")

  try: response = script_service.projects().getContent(scriptId=script_id).execute()
  except Exception:
    sys.exit("Could not get script project files")

  files = response.get("files", [])
  google_script = None

  for f in files:
    if f.get("name") == gs_filename and f.get("type") == "SERVER_JS":
      google_script = f.get("source")
      break

  if google_script is None: sys.exit("Failed to download google script")

  file_path = os.path.join(f"{os.getcwd()}/{output_dir}", f"{gs_filename}.gs")

  with open(file_path, "w", encoding="utf-8") as f:
    f.write(google_script)

  sys.exit("Google script downloaded")


if __name__ == "__main__":
  load_dotenv()
  flow = get_service_flow()
  if flow is None: raise ValueError("Error: could not create google oauth flow")
  creds = flow.run_local_server(port=0)
  download_gs(creds)