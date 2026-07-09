from collections.abc import Sequence
from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine, select

from med_tracker.config import get_settings
from med_tracker.exceptions import MedicationNotFoundError


# 1. Define shape of the data. My class inherits SQLModel, which inherits from Pydantic
class Medication(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    total_pills: int
    daily_dosage: int


# 2. We import the DB engine via function. First time it runs, engine is built and
# cached; later it always returns the cached one. This prevents actions environment-
# dependent when we import the med_tracker.database module for test purposes.
@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, echo=True)


# Function to physically create the file and tables when the app starts
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(get_engine())


# Get all medications function
def get_all_medications() -> Sequence[Medication]:
    with Session(get_engine()) as session:
        # select() fetches everything from the Medication table
        return session.exec(select(Medication)).all()


# Get one specific medication
def get_med(med_id: int) -> Medication:
    with Session(get_engine()) as session:
        med = session.get(Medication, med_id)
        if med is None:
            raise MedicationNotFoundError("Medication not found.")
    return med


# Add one new medication to the database
def add_med(med: Medication) -> Medication:
    with Session(get_engine()) as session:
        session.add(med)
        session.commit()
        session.refresh(med)  # Updates the object with the new ID
    return med


# Delete one medication based on id
def delete_med(med_id: int) -> str:
    with Session(get_engine()) as session:
        med = session.get(Medication, med_id)
        if med is None:
            raise MedicationNotFoundError(f"Medication {med_id} not found")
        name = med.name  # capture before deletion
        session.delete(med)
        session.commit()
    return name


# Take all daily medication
def take_all_daily_doses() -> Sequence[Medication]:
    with Session(get_engine()) as session:
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
