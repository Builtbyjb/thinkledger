from fastapi import APIRouter, Response, Form
from typing import Annotated
import os
from sendgrid import SendGridAPIClient
from utils.logger import log

router = APIRouter()

@router.post("/join-waitlist")
async def join_waitlist(
  firstname: Annotated[str, Form()],
  lastname: Annotated[str, Form()],
  email: Annotated[str, Form()]
) -> Response:
  # print(f"Received join waitlist request for {firstname} {lastname} ({email})")
  sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
  sendgrid_list_id = os.getenv("SENDGRID_LIST_ID")

  sg = SendGridAPIClient(api_key=sendgrid_api_key)

  data = {
    "list_ids": [sendgrid_list_id],
    "contacts": [{ "email": email, "first_name": firstname, "last_name": lastname}]
  }

  try:response = sg.client.marketing.contacts.put(request_body=data) # type: ignore
  except Exception as e:
    log.error(e)
    return Response(status_code=500)

  log.info(response.status_code, response.body)
  return Response(status_code=200)
