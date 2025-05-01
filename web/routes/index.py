from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, HTMLResponse
from web.middleware.authentication import auth_required
from web.content.features import FEATURES
from web.content.benefits import BENEFITS
from utils.styles import BTN_STYLE_FULL, BTN_STYLE_OUTLINE, HOVER
from utils.auth_utils import auth_session
from typing import Union

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/", response_model=None)
async def index(request: Request) -> Union[HTMLResponse, RedirectResponse]:
  session_id = request.cookies.get("session_id")
  if session_id:
    is_auth = auth_session(session_id)
    if is_auth: return RedirectResponse(url="/home", status_code=302)

  return templates.TemplateResponse(
    request=request,
    name="guest/index.html",
    context={
      "features": FEATURES,
      "benefits": BENEFITS,
      "btn_style_full": BTN_STYLE_FULL,
      "btn_style_outline": BTN_STYLE_OUTLINE
    }
  )


@router.get("/home")
@auth_required(mode="strict")
async def home(request: Request) -> HTMLResponse:
  username = request.state.username
  return templates.TemplateResponse(
    request=request,
    name="auth/home.html",
    context={"username": username, "hover": HOVER}
  )
