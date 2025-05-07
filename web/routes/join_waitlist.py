from fastapi import APIRouter, Response, Form, BackgroundTasks
from typing import Annotated
import os
from sendgrid import SendGridAPIClient
from utils.logger import log

router = APIRouter()


def handle_join_waitlist(firstname: str, lastname: str, email: str) -> None:
  sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
  sendgrid_list_id = os.getenv("SENDGRID_LIST_ID")

  sg = SendGridAPIClient(api_key=sendgrid_api_key)

  data = {
    "list_ids": [sendgrid_list_id],
    "contacts": [{ "email": email, "first_name": firstname, "last_name": lastname}]
  }

  # TODO: Better error handling
  try:response = sg.client.marketing.contacts.put(request_body=data)
  except Exception as e: log.error(f"Error adding user to waitlist: {e}")

  log.info(response.status_code, response.body)
  return None


@router.post("/join-waitlist")
async def join_waitlist(
  firstname: Annotated[str, Form()],
  lastname: Annotated[str, Form()],
  email: Annotated[str, Form()],
  bg: BackgroundTasks
) -> Response:
  # print(f"Received join waitlist request for {firstname} {lastname} ({email})")
  bg.add_task(handle_join_waitlist, firstname, lastname, email)
  return Response(status_code=200)
