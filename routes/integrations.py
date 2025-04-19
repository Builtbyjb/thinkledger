from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from middleware.authentication import auth_required

from utils.styles import BTN_STYLE_FULL


router = APIRouter(tags=["Integrations"])

templates = Jinja2Templates(directory="templates")

@router.get("/banking", status_code=status.HTTP_200_OK)
@auth_required(mode="strict")
async def banking(request: Request):
  username = request.state.username
  return templates.TemplateResponse(
    request=request,
    name="auth/banking.html",
    context={
      "username": username,
      "btn_style_full": BTN_STYLE_FULL
    }
  )


@router.get("/google", status_code=status.HTTP_200_OK)
@auth_required(mode="strict")
async def google(request: Request):
  username = request.state.username
  return templates.TemplateResponse(
    request=request,
    name="auth/google.html",
    context={
      "username": username,
      "btn_style_full": BTN_STYLE_FULL
    }
  )
