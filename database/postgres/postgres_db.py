from sqlmodel import create_engine, Session, SQLModel
import os
import sys
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")

# Create SQLModel engine
if POSTGRES_URL is not None:
    engine = create_engine(POSTGRES_URL, echo=True)
else:
    # Exit the program is a postgres connection url is not found
    sys.exit("Could not get postgres url from env variables")

# Dependency to get DB session
def get_db():
    with Session(engine) as session:
        yield session

# Function to create all tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
