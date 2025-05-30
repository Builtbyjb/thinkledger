import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.redis.redis import gen_redis
from dotenv import load_dotenv


def test_high_priority_task() -> None:
  return None


def add_task() -> bool:
  redis = gen_redis()
  if redis is None: return False
  access_token = os.getenv("DEMO_ACCESS_TOKEN")
  user_id = os.getenv("DEMO_USER_ID")
  value = f"transaction_sync:{access_token}"
  priority = "HIGH"
  with redis as r:
    # Add tasks to list head (LPUSH)
    try: r.lpush(f"tasks:{priority}:{user_id}", value)
    except Exception as e:
      print(f"Error adding task to queue: {e}")
      return False

  return True


if __name__ == "__main__":
  load_dotenv()
  print("Adding")
  if add_task(): print("Task added")
  else: print("Failed to add task")
