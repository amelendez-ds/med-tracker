import os
from collections.abc import Sequence

from dotenv import load_dotenv
from fastapi import HTTPException
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


# Get all medications function
def get_all_medications() -> Sequence[Medication]:
    with Session(engine) as session:
        # select() fetches everything from the Medication table
        return session.exec(select(Medication)).all()


# Get one specific medication
def get_med(med_id: int) -> Medication:
    with Session(engine) as session:
        med = session.get(Medication, med_id)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found")
    return med


# Add one new medication to the database
def add_med(med: Medication) -> Medication:
    with Session(engine) as session:
        session.add(med)
        session.commit()
        session.refresh(med)  # Updates the object with the new ID
    return med


# Delete one medication based on id
def delete_med(med_id: int) -> None:
    with Session(engine) as session:
        # Look up if the med exists
        med = get_med(med_id)

        # Delete the registry if it exists
        if med:
            session.delete(med)
            session.commit()


# Take all daily medication
def take_all_daily_doses() -> Sequence[Medication]:
    with Session(engine) as session:
        medications = session.exec(select(Medication)).all()

        for med in medications:
            # Automatically "take" the daily dose
            if med.total_pills >= med.daily_dosage:
                med.total_pills -= med.daily_dosage
            else:
                med.total_pills = 0  # Prevent negative numbers

            session.add(med)  # Save the new pill count
        session.commit()
        # OPTIMIZATION: Refresh and return the list so we don't have to query again
        for med in medications:
            session.refresh(med)

    return medications
