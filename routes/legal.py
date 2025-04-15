from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["Legal"])

templates = Jinja2Templates(directory="templates")


@router.get("/privacy-policy", status_code=status.HTTP_200_OK)
async def privacy_policy(request: Request):
    last_updated = "March 8, 2025"

    return templates.TemplateResponse(
        request=request,
        name="guest/privacy_policy.html",
        context={
            "last_updated": last_updated
        }
    )


@router.get("/terms-of-service", status_code=status.HTTP_200_OK)
async def terms_of_service(request: Request):
    last_updated = "March 8, 2025"

    return templates.TemplateResponse(
        request=request,
        name="guest/terms_of_service.html",
        context={
            "last_updated": last_updated
        }
    )
