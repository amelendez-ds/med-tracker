import os
from sqlmodel import Field, SQLModel, create_engine


# 1. Define shape of the data
class Medication(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    total_pills: int
    daily_dosage: int


# 2. Tell Python where to save the database file (in the 'data' folder!)
os.makedirs("data", exist_ok=True)  # This creates the folder if it doesn't exist
sqlite_file_name = "data/medications.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 3. Create the engine (translator between Python and SQLite)
# echo=True means it will print the raw SQL commands in the terminal to verify what's happening
engine = create_engine(sqlite_url, echo=True)


# 4. Function to physically create the file and tables when the app starts
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
