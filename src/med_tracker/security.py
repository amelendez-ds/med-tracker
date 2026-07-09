from fastapi import HTTPException

from med_tracker.config import get_settings


def verify_authorized_cron(authorization: str | None) -> None:
    # Security Check: Is this the authorized Alarm Clock?
    if authorization != f"Bearer {get_settings().cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized access!")
