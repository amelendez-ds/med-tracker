def calculate_days_left(total_pills: int, daily_dosage: int) -> int:
    # Use floor division to get the whole days and return int
    return total_pills // daily_dosage


def is_low_stock(days_left: int, threshold_days: int) -> bool:
    return days_left <= threshold_days


def find_low_stock(medications, threshold_days=14) -> dict:
    low_stock_meds = {}
    for med in medications:
        days_left = calculate_days_left(med.total_pills, med.daily_dosage)
        if is_low_stock(days_left, threshold_days):
            low_stock_meds[med.name] = days_left
    return low_stock_meds
