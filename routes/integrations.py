from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates

from utils.styles import BTN_STYLE_FULL


router = APIRouter(tags=["Integrations"])

templates = Jinja2Templates(directory="templates")

@router.get("/banking", status_code=status.HTTP_200_OK)
async def banking(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/banking.html",
        context={
            "btn_style_full": BTN_STYLE_FULL
        }
    )


@router.get("/google", status_code=status.HTTP_200_OK)
async def google(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/google.html",
        context={
            "btn_style_full": BTN_STYLE_FULL
        }
    )
