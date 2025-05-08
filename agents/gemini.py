from utils.logger import log
import os
import json
from google import genai
from typing import Any


def gemini_response(prompt: str) -> Any:
  gemini_api_key = os.getenv("GEMINI_API_KEY")
  client = genai.Client(api_key=gemini_api_key)
  return client.models.generate_content(
      model="gemini-2.5-flash",
      contents=f"{prompt}"
  )


def sanitize_gemini_response(response) -> Any:
  cleaned_response_text = response.text.strip().strip('`').strip()
  if cleaned_response_text.lower().startswith("json"):
      cleaned_response_text = cleaned_response_text[4:].strip()

  log.info(f"Gemini Raw Response:\n{cleaned_response_text}")
  return json.loads(cleaned_response_text)