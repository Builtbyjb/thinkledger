from typing import Callable, Any
from functools import wraps
import time
from utils.util import time_format
from utils.context import DEBUG
from utils.logger import log


def perf(func:Callable[..., Any]) -> Callable[..., Any]:
  """
  Logs how long a function takes to execute
  """
  @wraps(func)
  def wrapper(*args, **kwargs) -> Any:
    start = time.perf_counter()
    results = func(*args, **kwargs)
    end = time.perf_counter()
    if DEBUG >= 1: log.info(f"{func.__name__} took {time_format(end - start)}")
    return results
  return wrapper
