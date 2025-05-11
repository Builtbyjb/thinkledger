import os
import json
from google import genai
from typing import Any
from utils.types import JournalEntry


def gemini_response(prompt: str) -> Any:
  # TODO: Add system instructions
  gemini_api_key = os.getenv("GEMINI_API_KEY")
  client = genai.Client(api_key=gemini_api_key)
  return client.models.generate_content(
    # model = "gemini-2.5-pro-preview-05-06",
    # model = "gemini-2.5-flash-preview-04-17",
    model = "gemini-2.0-flash",
    contents=f"{prompt}"
  )


def sanitize_gemini_response(response) -> JournalEntry:
  cleaned_response = response.text.strip().strip('`').strip()
  if cleaned_response.lower().startswith("json"):
    cleaned_response = cleaned_response[4:].strip()
  # log.info(f"Gemini Raw Response:\n{cleaned_response}")
  return JournalEntry(**json.loads(cleaned_response))