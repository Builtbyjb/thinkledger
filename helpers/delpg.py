#!/usr/bin/env python3

#########################################################################################
# WARNING: This script deletes table(s) from a postgreSQL database. Use carefully!!!
#########################################################################################

import os, sys
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from sqlmodel import create_engine


def delete() -> None:
  """
    Deletes a postgres table. The script takes in a table
    as command line arguments

    chmod +x delscript.py to create an executable script
  """
  postgres_url = os.getenv("POSTGRES_URL")
  if postgres_url is not None: engine = create_engine(postgres_url)
  else: sys.exit("Could not get postgres url from env variables")
  # TODO: Add ability to delete multiple tables
  if len(sys.argv) != 2: sys.exit("Usage: ./delscript.py <table_name>")
  table_name = sys.argv[1]
  print(f"Deleting {table_name} table")
  try:
    with engine.connect() as db:
      db.exec_driver_sql(f"DROP TABLE {table_name}")
      db.commit()
  except Exception as e: sys.exit(f"Error deleting table: {e}")
  print(f"Deleted {table_name} table")
  return None


if __name__ == "__main__":
  load_dotenv()
  delete()
