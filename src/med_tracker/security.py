import os

from fastapi import HTTPException

# Load the secret key that protects our daily job
CRON_SECRET = os.getenv("CRON_SECRET")


def verify_authorised_cron(authorization: str | None) -> None:
    # Security Check: Is this the authorized Alarm Clock?
    if authorization != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized access!")
