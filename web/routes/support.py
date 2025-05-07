from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from web.content.faq import FAQs
from web.content.support_categories import SUPPORT_CATEGORIES
from utils.styles import BTN_STYLE_FULL, LINK_TEXT_STYLE, LINK_ICON_STYLE


router = APIRouter(prefix="/support", tags=["Support"])
templates = Jinja2Templates(directory="web/templates")


@router.get("/", status_code=status.HTTP_200_OK, response_model=None)
async def support(request: Request) -> HTMLResponse:
  return templates.TemplateResponse(
    request=request,
    name="guest/support.html",
    context={
      "categories": SUPPORT_CATEGORIES,
      "faqs": FAQs,
      "btn_style_full": BTN_STYLE_FULL,
      "link_text_style": LINK_TEXT_STYLE,
    }
  )


@router.get("/bookkeeping", status_code=status.HTTP_200_OK)
async def support_bookkeeping(request: Request) -> HTMLResponse:
  return templates.TemplateResponse(
    request=request,
    name="guest/support_bookkeeping.html",
    context={"link_icon_style": LINK_ICON_STYLE}
  )


@router.get("/financial-reports", status_code=status.HTTP_200_OK)
async def support_financial_reports(request: Request) -> HTMLResponse:
  return templates.TemplateResponse(
    request=request,
    name="guest/support_financial_reports.html",
    context={"link_icon_style": LINK_ICON_STYLE}
  )


@router.get("/analytics-insights", status_code=status.HTTP_200_OK)
async def support_analytics_insights(request: Request) -> HTMLResponse:
  return templates.TemplateResponse(
    request=request,
    name="guest/support_analytics_insights.html",
    context={"link_icon_style": LINK_ICON_STYLE}
  )
