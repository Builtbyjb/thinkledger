from fastapi import APIRouter

router = APIRouter()

# Get google service token
@router.get("/auth-google-service")
async def google_service_token():
    return {"token": "example_token"}
