from enum import Enum
from database.redis.redis import gen_redis


class Tasks(Enum):
  trans_sync = "transaction_sync"

class TaskPriority(Enum):
  """
    HIGH priority tasks are tasks that require immediate user feedback.
    LOW priority tasks are tasks that go on in the background without direct user input
  """
  HIGH = "HIGH"
  LOW = "LOW"

def add_tasks(value: str, user_id: str, priority: TaskPriority) -> bool:
  """
    Adds a task to the core task queue.
    Value is a string containing the task function signature, and its arguments,
    separated by a colon e.g "func:arg1:arg2"
  """
  redis = gen_redis()
  if redis is None:
    print("Unable to get redis @add_task > core_utils.py")
    return False

  # Add tasks to list head (LPUSH)
  try: redis.lpush(f"tasks:{priority}:{user_id}", value)
  except Exception as e:
    print(f"Error adding task to queue: {e}")
    return False

  return True

def invert_amount(amount: float) -> float:
  """
    Inverts the amount to be negative if it is positive, and positive if it is negative
  """
  if amount > 0: return -amount
  else: return abs(amount)