from collections.abc import Sequence

from fastapi import HTTPException

from med_tracker.database import Medication


def calculate_days_left(total_pills: int, daily_dosage: int) -> int:
    # Use floor division to get the whole days and return int
    return total_pills // daily_dosage


def is_low_stock(days_left: int, threshold_days: int) -> bool:
    return days_left <= threshold_days


def find_low_stock(
    medications: Sequence[Medication], threshold_days: int = 14
) -> dict[str, int]:
    low_stock_meds: dict[str, int] = {}
    for med in medications:
        if med.daily_dosage <= 0:
            continue
        days_left = calculate_days_left(med.total_pills, med.daily_dosage)
        if is_low_stock(days_left, threshold_days):
            low_stock_meds[med.name] = days_left
    return low_stock_meds


def verify_enough_stock(medication: Medication) -> None:
    # Check the pills specifically for this 'take' action
    if medication.total_pills < medication.daily_dosage:
        raise HTTPException(
            status_code=400, detail="Not enough pills left! Time to refill."
        )
