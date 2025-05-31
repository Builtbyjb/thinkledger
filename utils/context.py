import os
from typing import ClassVar


class ContextVar:
  _cache: ClassVar[dict[str, 'ContextVar']] = {}
  value: int
  key: str
  def __init__(self, key, default_value):
    if key in ContextVar._cache: raise RuntimeError(f"Attempt to recreate ContextVar {key}")
    ContextVar._cache[key] = self
    env_var = str(os.getenv(key, default_value))
    self.key, self.value = key, int(env_var) if len(env_var) > 0 else 0
    # print(self.key, self.value)

  def __bool__(self): return bool(self.value)
  def __ge__(self, x): return self.value >= x
  def __gt__(self, x): return self.value > x
  def __lt__(self, x): return self.value < x
  def __le__(self, x): return self.value <= x
  def __eq__(self, x): return self.value == x
  def __repr__(self): return f"ContextVar(key='{self.key}', value={self.value})"


DEBUG = ContextVar("DEBUG", 0)