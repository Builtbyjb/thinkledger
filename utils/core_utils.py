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

def add_tasks(task: Tasks, user_id: str, prority: TaskPriority) -> bool:
  """
    Adds a task to the core task queue.
  """
  redis = gen_redis()
  if redis is None:
    print("Unable to get redis @add_task > core_utils.py")
    return False

  # Add tasks to list head (LPUSH)
  try:
    redis.lpush(f"tasks:{prority}:{user_id}", str(task.value))
  except Exception as e:
    print(f"Error adding task to queue: {e}")
    return False

  return True
