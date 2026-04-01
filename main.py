from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from database import create_db_and_tables, engine, Medication
from notifications import send_low_stock_alert


# This "lifespan" function runs before the API starts accepting requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Creating database tables...")
    create_db_and_tables()
    yield
    print("Shutting down...")


# Initialise FastAPI and attach the lifespan
app = FastAPI(lifespan=lifespan)


# 1. CREATE: Add a new medication to the database
@app.post("/medications/", response_model=Medication)
def add_medication(med: Medication):
    with Session(engine) as session:
        session.add(med)
        session.commit()
        session.refresh(med)  # Updates the object with the new ID
        return med


# 2. READ: Get a list of all my medications
@app.get("/medications/", response_model=list[Medication])
def get_medications():
    with Session(engine) as session:
        # select() fetches everything from the Medication table
        medications = session.exec(select(Medication)).all()
        return medications


# 3. UPDATE: Log that I took my daily dose
@app.put("/medications/{med_id}/take")
def take_medication(med_id: int):
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
@app.put("/medications/{med_id}/refil")
def refill_medication(med_id: int, amount: int):
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


# 5. BUSINESS LOGIC: Check all stock and trigger alerts
@app.get("/check-stock")
def check_all_stock():
    alerts_triggered = []

    with Session(engine) as session:
        medications = session.exec(select(Medication)).all()

        for med in medications:
            # Prevent division by zero just in case
            if med.daily_dosage > 0:
                # Use floor division (//) to get whole days
                days_remaining = med.total_pills // med.daily_dosage

                if days_remaining <= 14:
                    send_low_stock_alert(med.name, days_remaining)
                    alerts_triggered.append(med.name)
    return {
        "message": "Daily stock check complete.",
        "alerts_sent_for": alerts_triggered,
    }
