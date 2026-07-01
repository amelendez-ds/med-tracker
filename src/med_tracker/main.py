from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header

from med_tracker.alerts import notify_low_stock, verify_authorised_cron
from med_tracker.core.stock import find_low_stock, verify_enough_stock
from med_tracker.database import (
    Medication,
    add_med,
    create_db_and_tables,
    delete_med,
    get_all_medications,
    get_med,
    take_all_daily_doses,
)


# This "lifespan" function runs before the API starts accepting requests
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Starting up: Creating database tables...")
    create_db_and_tables()
    yield
    print("Shutting down...")


# Initialise FastAPI and attach the lifespan
app = FastAPI(lifespan=lifespan)


# Route 1. CREATE: Add a new medication to the database
@app.post("/medications/", response_model=Medication)
def add_medication(med: Medication) -> Medication:
    return add_med(med)


# Route 2. READ: Get a list of all my medications
@app.get("/medications/", response_model=list[Medication])
def get_medications() -> Sequence[Medication]:
    return get_all_medications()


# Route 3. UPDATE: Log that I took my daily dose manually
@app.put("/medications/{med_id}/take")
def take_medication(med_id: int) -> dict:
    med = get_med(med_id)
    verify_enough_stock(med)
    med.total_pills -= med.daily_dosage
    add_med(med)
    return {
        "message": f"Dose taken! {med.total_pills} pills remaining.",
        "medication": med,
    }


# Route 4. DELETE: Remove a specific medication
@app.delete("/medications/")
def delete_medication(med_id: int) -> dict:
    med = get_med(med_id)
    delete_med(med_id)
    return {"message": f"Medication {med.name} was sucessfully deleted."}


# Route 5. UPDATE: Refill an empty medication
@app.put("/medications/{med_id}/refill")
def refill_medication(med_id: int, amount: int) -> dict:
    med = get_med(med_id)
    med.total_pills += amount
    add_med(med)
    return {"message": f"{med.name} refilled. Total is now {med.total_pills}."}


# Route 6. LOGIC: Check all stock manually and trigger alerts
@app.get("/check-stock")
def check_all_stock() -> dict:
    medications = get_all_medications()
    low_stock_meds = find_low_stock(medications, threshold_days=14)
    for med_name, days_left in low_stock_meds.items():
        notify_low_stock(med_name, days_left)
    return {
        "message": "Daily stock check complete.",
        "alerts_sent_for": ", ".join(low_stock_meds.keys()),
    }


# Route 7. AUTOMATION: Daily Job to deduct pills and check stock
@app.post("/daily-automation/")
def run_daily_automation(authorization: str | None = Header(None)) -> dict:
    # If this fails, it raises an HTTPException and stops execution automatically
    verify_authorised_cron(authorization)
    # 1. Take the doses and get the updated list back
    medications = take_all_daily_doses()
    # 2. Check for low stock
    low_stock_meds = find_low_stock(medications, threshold_days=14)
    # 3. Send notifications
    for med_name, days_left in low_stock_meds.items():
        notify_low_stock(med_name, days_left)
    return {
        "message": "Daily automation complete.",
        "alerts_sent_for": ", ".join(low_stock_meds.keys()) or "None",
    }
