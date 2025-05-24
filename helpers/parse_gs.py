import os, sys, re
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import GS_FILENAME
from typing import List


# TODO: Generate a uuid and append assign it to the current user and embed it to the google script
# TODO: Check lines for variable and replace variables with values before appending
def replace_str(line:str) -> str:
  p = rf"\b{re.escape('__DEBUG__')}\b"
  return re.sub(p, "1", line)


#  The function could take in a user id,
def google_script() -> str:
  root_dir = str(Path(__file__).parent.parent)
  file_path = os.path.join(f"{root_dir}/{GS_FILENAME}", f"{GS_FILENAME}.gs")

  lines:List[str] = []

  with open(file_path, "r", encoding="utf-8") as f:
    for l in f:
      new_l = replace_str(l)
      lines.append(new_l)

  return "\n".join(lines)


if __name__ == "__main__":
  print(google_script())
