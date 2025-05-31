from enum import Enum
from database.redis.redis import gen_redis


class Tasks(Enum):
  setup_spreadsheet = "setup_spreadsheet"
  sync_transaction = "sync_transaction"


class TaskPriority(Enum):
  """
    HIGH priority tasks are tasks that require immediate user feedback.
    LOW priority tasks are tasks that go on in the background without direct user input
  """
  HIGH = "HIGH"
  LOW = "LOW"


def add_task(value: str, user_id: str, priority: TaskPriority) -> bool:
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


def get_task(v:str) -> str: return v.split(":")[0]


def get_task_args(v:str) -> list[str]: return v.split(":")[1:]