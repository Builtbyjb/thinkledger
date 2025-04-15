import os
from google_auth_oauthlib.flow import Flow


# Google user authentication oauth configuration
def sign_in_auth_config() -> Flow:
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    CLIENT_ID = os.getenv("GOOGLE_SIGNIN_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_SIGNIN_CLIENT_SECRET")
    REDIRECT_URL = os.getenv("GOOGLE_SIGNIN_REDIRECT_URL")
    # SERVER_URL = os.getenv("SERVER_URL")

    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
             "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [REDIRECT_URL],
        }
    }

    config = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URL
    )

    return config


# Google access grant oauth configuration
def service_auth_config() -> Flow:
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    CLIENT_ID = os.getenv("GOOGLE_SERVICE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_SERVICE_CLIENT_SECRET")
    REDIRECT_URL = os.getenv("GOOGLE_SERVICE_REDIRECT_URL")
    # SERVER_URL = os.getenv("SERVER_URL")

    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
             "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [REDIRECT_URL],
        }
    }

    config = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URL
    )

    return config
