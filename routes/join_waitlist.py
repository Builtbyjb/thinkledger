from fastapi import APIRouter, Response, Form
from typing import Annotated
import os
from sendgrid import SendGridAPIClient

router = APIRouter()

@router.post("/join-waitlist")
async def join_waitlist(
    firstname: Annotated[str, Form()],
    lastname: Annotated[str, Form()],
    email: Annotated[str, Form()]
) -> Response:
    # print(f"Received join waitlist request for {firstname} {lastname} ({email})")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_LIST_ID = os.getenv("SENDGRID_LIST_ID")

    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)

    data = {
        "list_ids": [SENDGRID_LIST_ID],
        "contacts": [
            {
                "email": email,
                "first_name": firstname,
                "last_name": lastname,
            }
        ]
    }

    try:
        response = sg.client.marketing.contacts.put(request_body=data) # type: ignore
    except Exception as e:
        print(e)
        return Response(status_code=500)

    print(response.status_code)
    print(response.body)
    return Response(status_code=200)
