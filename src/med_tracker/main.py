import os
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from sqlmodel import Session, select

from med_tracker.database import Medication, create_db_and_tables, engine
from med_tracker.notifications import notify_low_stock

# Load the secret key that protects our daily job
CRON_SECRET = os.getenv("CRON_SECRET")


# This "lifespan" function runs before the API starts accepting requests
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Starting up: Creating database tables...")
    create_db_and_tables()
    yield
    print("Shutting down...")


# Initialise FastAPI and attach the lifespan
app = FastAPI(lifespan=lifespan)


# 1. CREATE: Add a new medication to the database
@app.post("/medications/", response_model=Medication)
def add_medication(med: Medication) -> Medication:
    with Session(engine) as session:
        session.add(med)
        session.commit()
        session.refresh(med)  # Updates the object with the new ID
        return med


# 2. READ: Get a list of all my medications
@app.get("/medications/", response_model=list[Medication])
def get_medications() -> Sequence[Medication]:
    with Session(engine) as session:
        # select() fetches everything from the Medication table
        medications = session.exec(select(Medication)).all()
        return medications


# 3. UPDATE: Log that I took my daily dose manually
@app.put("/medications/{med_id}/take")
def take_medication(med_id: int) -> dict:
    with Session(engine) as session:
        med = session.get(Medication, med_id)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found")
        if med.total_pills < med.daily_dosage:
            raise HTTPException(
                status_code=400, detail="Not enough pills left! Time to refill."
            )

        med.total_pills -= med.daily_dosage
        session.add(med)
        session.commit()
        session.refresh(med)
        return {
            "message": f"Dose taken! {med.total_pills} pills remaining.",
            "medication": med,
        }


# 4. UPDATE: Refill an empty medication
@app.put("/medications/{med_id}/refill")
def refill_medication(med_id: int, amount: int) -> dict:
    with Session(engine) as session:
        med = session.get(Medication, med_id)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found")

        med.total_pills += amount
        session.add(med)
        session.commit()
        session.refresh(med)
        return {
            "message": f"Refilled {amount} pills. Total is now {med.total_pills}.",
            "medication": med,
        }


# 5. LOGIC: Check all stock manually and trigger alerts
@app.get("/check-stock")
def check_all_stock() -> dict:
    alerts_triggered = []

    with Session(engine) as session:
        medications = session.exec(select(Medication)).all()

        for med in medications:
            # Prevent division by zero just in case
            if med.daily_dosage > 0:
                # Use floor division (//) to get whole days
                days_remaining = med.total_pills // med.daily_dosage

                if days_remaining <= 14:
                    notify_low_stock(med.name, days_remaining)
                    alerts_triggered.append(med.name)
    return {
        "message": "Daily stock check complete.",
        "alerts_sent_for": alerts_triggered,
    }


# 6. AUTOMATION: Daily Job to deduct pills and check stock
@app.post("/daily-automation/")
def run_daily_automation(authorization: str | None = Header(None)) -> dict:
    # Security Check: Is this the authorized Alarm Clock?
    if authorization != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized access!")

    alerts_triggered = []

    with Session(engine) as session:
        medications = session.exec(select(Medication)).all()

        for med in medications:
            # Automatically "take" the daily dose
            if med.total_pills >= med.daily_dosage:
                med.total_pills -= med.daily_dosage
            else:
                med.total_pills = 0  # Prevent negative numbers

            session.add(med)  # Save the new pill count

            # Check if stock is low (14 days or less)
            if med.daily_dosage > 0:
                days_remaining = med.total_pills // med.daily_dosage
                if days_remaining <= 14:
                    notify_low_stock(med.name, days_remaining)
                    alerts_triggered.append(med.name)

        session.commit()  # Push all changes to Neon database

    return {"message": "Daily automation complete.", "alerts_sent": alerts_triggered}
