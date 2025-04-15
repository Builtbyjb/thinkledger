from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta, timezone
import os
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from utils.util import generate_crypto_string
from sqlmodel import Session
from database.postgres.postgres_db  import get_db
from database.redis.redis import get_redis_client
from database.postgres.postgres_schema import User


router = APIRouter(prefix="/auth/google/callback")

TOKEN_URL = "https://oauth2.googleapis.com/token"

@router.get("/sign-in")
async def google_sign_in_callback(
    request: Request,
    db: Session = Depends(get_db),
    redis = Depends(get_redis_client)
):
    # Verify state parameter
    if request.query_params.get("state") != request.cookies.get("state"):
        print("Invalid state parameter")
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    CLIENT_ID = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("GOOGLE_SIGNIN_REDIRECT_URI")

    code = request.query_params.get("code")

    payload = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get access token")

    token = response.json()

    try:
        user_info = id_token.verify_oauth2_token(
            token["id_token"],
            google_requests.Request(),
            CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_id = user_info.get("sub")
    username = user_info.get("name")
    access_token = token["access_token"]
    refresh_token = token["refresh_token"]
    session_id: str = generate_crypto_string()

    # Check if the user exists before adding to database
    user = db.get(User, user_id)
    if not user:
        # Save userinfo to postgres database
        new_user = User(
            id=user_id,
            email=user_info.get("email"),
            name=username,
            given_name=user_info.get("givenName"),
            family_name=user_info.get("familyName"),
            picture=user_info.get("picture"),
            locale=user_info.get("locale")
        )

        try:
            db.add(new_user)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal server error")

        db.commit()
        db.refresh(new_user)

        # Save userinfo to redis database
        try:
            redis.set(session_id, user_id)
            redis.set(f"username:{user_id}", username)
            redis.set(f"user_id:{user_id}", user_id) # For use later
            redis.set(f"username:{user_id}", username)
            redis.set(f"access_token:{user_id}", access_token)
            if refresh_token is not None:
                redis.set(f"refresh_token:{user_id}", refresh_token)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal server error")
    else:
        try:
            redis.set(session_id, user_id)
            redis.set(f"access_token:{user_id}", access_token)
            if refresh_token is not None:
                redis.set(f"refresh_token:{user_id}", refresh_token)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    # result = redis.delete("username:123")
    # if result > 0:
    #     print("Key successfully deleted")
    # else:
    #     print("Key did not exist")

    # Set user authentication cookie
    response = RedirectResponse(url="/home", status_code=302)
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    response.set_cookie(
        key="session_id",
        value=session_id,
        expires=expires,
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )


@router.get("/services")
async def google_service_callback(request: Request):
    pass
