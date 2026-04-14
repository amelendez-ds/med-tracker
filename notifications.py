import os

import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
MY_EMAIL = os.getenv("EMAIL_ADDRESS")


def send_email_alert(med_name: str, days_left: int):
    """Sends a real email alert if stock is low via HTTP API."""

    if not RESEND_API_KEY or not MY_EMAIL:
        print(f"Terminal Alert: {med_name} is low. Credentials missing.")
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    # Resend allows me to use a testing email address 'onboarding@resend.dev'
    # to send emails to the address I verified my account with.
    payload = {
        "from": "onboarding@resend.dev",
        "to": MY_EMAIL,
        "subject": f"Medication Alert: Low stock for {med_name}",
        "html": (
            f"<p>Time to refill <strong>{med_name}</strong>! "
            f"You only have {days_left} days of stock remaining.</p>"
        ),
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an error for bad status codes
        print(f"Alert email sent successfully for {med_name}!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_discord_alert(med_name: str, days_left: int):
    """Sends a push notification to Discord."""

    if not DISCORD_WEBHOOK:
        print("Webhook URL missing.")
        return

    message = {
        "content": (
            f"🚨 **Medication Alert:** Time to refill **{med_name}**! "
            f"You only have {days_left} days of stock remaining."
        ),
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=message)
        response.raise_for_status()
        print(f"Alert sent successfully for {med_name}!")
    except Exception as e:
        print(f"Failed to send alert: {e}")


def notify_low_stock(med_name: str, days_left: int):
    """Triggers all notification channels for low stock."""
    print(f"Triggering alerts for {med_name}...")

    send_email_alert(med_name, days_left)
    send_discord_alert(med_name, days_left)

    print(f"Finished sending all alerts for {med_name}.")
