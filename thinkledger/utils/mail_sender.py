import os
import smtplib
from sendgrid import SendGridAPIClient
from utils.context import DEBUG
from utils.logger import log
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailSender:
  def __init__(self, sendgrid=False):
    if sendgrid:
      self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
      self.sendgrid_list_id = os.getenv("SENDGRID_LIST_ID")
    else:
      self.app_password = os.getenv("GMAIL_APP_PASSWORD")
      self.email = os.getenv("GMAIL_ADDRESS")
      self.smtp_server = "smtp.gmail.com"
      self.smtp_port = 587

  def handle_gmail(self, email: str, subject: str, content: str, html: bool=False) -> bool:
    """Send emails using gmail"""
    if self.app_password is None:
      log.error("Missing Gmail app password")
      return False

    if self.email is None:
      log.error("Missing Gmail email address")
      return False

    try:
      if DEBUG >= 1: log.info("Sending email...")
      msg = MIMEMultipart('alternative')
      msg['From'] = "Thinkledger <info@thinkledger.app>"
      msg['To'] = email
      msg['Subject'] = subject

      # Create HTML version if html is True
      if html:
        html_part = MIMEText(content, 'html')
        msg.attach(html_part)
      else:
        text_part = MIMEText(content, 'plain')
        msg.attach(text_part)

      # Send email
      with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        server.starttls()  # Enable encryption
        server.login(self.email, self.app_password)
        server.send_message(msg)

      if DEBUG >= 1: log.info(f"HTML email sent successfully to {email}")
      return True

    except Exception as e:
      print(f"Error sending email: {e}")
      return False

  def handle_sendgrid(self, firstname: str, lastname: str, email: str) -> None:
    """ Sends emails using sendgrid"""
    if self.sendgrid_api_key is None or self.sendgrid_list_id is None:
      log.error("Missing SendGrid API key or list ID")
      return None

    data = {
      "list_ids": [self.sendgrid_list_id],
      "contacts": [{
        "email": email,
        "first_name": firstname,
        "last_name": lastname
      }]
    }

    try:
      sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
      response = sg.client.marketing.contacts.put(request_body=data)
      log.info(response.status_code, response.body)
    except Exception as e:
      log.error(f"Error adding user to waitlist: {e}")

    return None
