import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.gemini import gemini_response
from prompt.journal_entry import generate_prompt
from database.redis.redis import gen_redis
from dotenv import load_dotenv


def add_task() -> bool:
  redis = gen_redis()
  if redis is None: return False
  access_token = os.getenv("DEMO_ACCESS_TOKEN")
  user_id = os.getenv("DEMO_USER_ID")
  value = f"setup_spreadsheet:{access_token}"
  priority = "HIGH"
  with redis as r:
    # Add tasks to list head (LPUSH)
    try: r.lpush(f"task:{priority}:{user_id}", value)
    except Exception as e:
      print(f"Error adding task to queue: {e}")
      return False
  return True


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
  load_dotenv()
  if add_task(): print("Task added")
  else: print("Failed to add task")