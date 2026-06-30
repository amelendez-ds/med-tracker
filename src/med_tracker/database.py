import os
from collections.abc import Sequence

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Load the secret variables from the .env file (for local testing)
load_dotenv()


# 1. Define shape of the data. My class inherits SQLModel, which inherits from Pydantic
class Medication(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    total_pills: int
    daily_dosage: int


# 2. Grab the Neon URL from the environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError(
        "DATABASE_URL is missing! Check your .env file or Render environment variables."
    )

# 3. Create the engine and connect it to where my (Neon) database lives
engine = create_engine(database_url, echo=True)


# Function to physically create the file and tables when the app starts
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_all_medications() -> Sequence[Medication]:
    with Session(engine) as session:
        # select() fetches everything from the Medication table
        medications = session.exec(select(Medication)).all()
        return medications
