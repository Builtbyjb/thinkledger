import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.gemini import gemini_response
from prompt.journal_entry import generate_prompt


def test_gemini_response() -> None:
  prompt = generate_prompt({
    "date": "2025-06-11",
    "amount": "50",
    "detail": "transportation",
    "payment_channel": "online",
    "merchant_name": "uber",
    "pending": "false",
  })
  response = gemini_response(prompt)
  print(response)


if __name__ == "__main__":
  test_gemini_response()