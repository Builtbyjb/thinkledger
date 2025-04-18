from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from templates.content.faq import FAQs
from templates.content.support_categories import SUPPORT_CATEGORIES
from utils.styles import BTN_STYLE_FULL, LINK_TEXT_STYLE, LINK_ICON_STYLE


router = APIRouter(
    prefix="/support",
    tags=["Suppport"],
)

templates = Jinja2Templates(directory="templates")


@router.get("/", status_code=status.HTTP_200_OK)
async def support(request: Request):
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
async def support_bookkeeping(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="guest/support_bookkeeping.html",
        context={
            "link_icon_style": LINK_ICON_STYLE,
        }
    )


@router.get("/financial-reports", status_code=status.HTTP_200_OK)
async def support_financial_reports(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="guest/support_financial_reports.html",
        context={
            "link_icon_style": LINK_ICON_STYLE,
        }
    )


@router.get("/analytics-insights", status_code=status.HTTP_200_OK)
async def support_analytics_insights(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="guest/support_analytics_insights.html",
        context={
            "link_icon_style": LINK_ICON_STYLE,
        }
    )
