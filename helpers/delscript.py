#!/usr/bin/env python3

from sqlmodel import create_engine
import os
import sys
from dotenv import load_dotenv

def delete():
  """
    Deletes a postgres table. The script takes in a table
    as command line arguments

    chmod +x delscript.py to create an executable script
  """
  POSTGRES_URL = os.getenv("POSTGRES_URL")
  if POSTGRES_URL is not None: engine = create_engine(POSTGRES_URL)
  else: sys.exit("Could not get postgres url from env variables")
  if len(sys.argv) != 2: sys.exit("Usage: ./delscript.py <table_name>")
  table_name = sys.argv[1]
  print(f"Deleting {table_name} table")
  try:
    with engine.connect() as db:
      db.exec_driver_sql(f"DROP TABLE {table_name}")
      db.commit()
  except Exception as e: sys.exit(f"Error deleting table: {e}")
  sys.exit(f"Deleted {table_name} table")

if __name__ == "__main__":
  load_dotenv()
  delete()
