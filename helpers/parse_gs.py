import os, sys, re
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import GS_FILENAME
from typing import List
from utils.context import DEBUG
import uuid
from redis import Redis


def replace_str(line:str, user_id:str, redis:Redis) -> str:
  url = f"{os.getenv('SERVER_URL')}/google/spreadsheet/signal"

  new_line = ""

  debug = re.escape("SET_DEBUG__()")
  level = "1" if DEBUG >= 1 else "0"
  if bool(re.search(debug, line)): new_line = re.sub(debug, level, line)

  tmp_user_id = re.escape("SET_TMP_USER_ID__()")
  if bool(re.search(tmp_user_id, line)):
    tmp_id = str(uuid.uuid4())
    if DEBUG < 2:
      try: redis.set(f"spreadsheet:{tmp_id}", user_id)
      except Exception as e: raise Exception(f"Error saving tmp id to redis: {e}")
    new_line = re.sub(tmp_user_id, '\"' + tmp_id +'\"', line)

  backend_url = re.escape("SET_BACKEND_URL__()")
  if bool(re.search(backend_url, line)): new_line = re.sub(backend_url,'\"' + url + '\"', line)

  return new_line if len(new_line) > 0 else line


def google_script(user_id:str, redis:Redis) -> str:
  root_dir = str(Path(__file__).parent.parent)
  file_path = os.path.join(f"{root_dir}/{GS_FILENAME}", f"{GS_FILENAME}.gs")

  lines:List[str] = []

  with open(file_path, "r", encoding="utf-8") as f:
    for l in f:
      new_l = replace_str(l, user_id, redis)
      lines.append(new_l)

  return "\n".join(lines)


if __name__ == "__main__":
  print("Action required")
  # print(google_script("1"))
