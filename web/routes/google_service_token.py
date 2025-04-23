from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from enum import Enum
from utils.auth_utils import service_auth_config
from datetime import datetime, timedelta, timezone


router = APIRouter()


class GoogleScopes(Enum):
  sheets = "https://www.googleapis.com/auth/spreadsheets"
  drive = "https://www.googleapis.com/auth/drive.file"


# Get google service token
@router.get("/auth-google-service")
async def google_service_token(request: Request) -> JSONResponse:
  scopes: list[str] = []

  google_sheet = request.query_params.get("google_sheet")
  google_drive = request.query_params.get("google_drive")

  if google_sheet == "true": scopes.append(GoogleScopes.sheets.value)
  if google_drive == "true": scopes.append(GoogleScopes.drive.value)

  if len(scopes) == 0: return JSONResponse(
    content={"error": "No scopes provided"},
    status_code=400,
  )

  # Get oauth service config
  config = service_auth_config(scopes)
  url, state = config.authorization_url(
     #  access_type="offline",
     # include_granted_scopes="true",
     # prompt="consent"
  )

  response = JSONResponse(content={"url": url}, status_code=200)
  expires = datetime.now(timezone.utc) + timedelta(minutes=5)
  response.set_cookie(
      key="state",
      value=state,
      expires=expires,
      path="/",
      secure=True,
      httponly=True,
      samesite="lax"
  )
  return response
