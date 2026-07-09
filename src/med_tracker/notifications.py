from collections.abc import Sequence
from typing import Protocol

import requests

from med_tracker.config import get_settings

# from dotenv import load_dotenv

# # This needs to be loaded before getting env variables
# load_dotenv()

# EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
# RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


class NotificationChannel(Protocol):
    """The contract every alert channel must satisfy."""

    def send(self, med_name: str, days_left: int) -> None: ...


class EmailChannel:
    def send(self, med_name: str, days_left: int) -> None:
        if not get_settings().resend_api_key or not get_settings().email_address:
            print(f"Terminal Alert: {med_name} is low. Credentials missing.")
            return

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {get_settings().resend_api_key}",
            "Content-Type": "application/json",
        }

        # Resend allows me to use a testing email address 'onboarding@resend.dev'
        # to send emails to the address I verified my account with.
        payload = {
            "from": "onboarding@resend.dev",
            "to": get_settings().email_address,
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


class DiscordChannel:
    def send(self, med_name: str, days_left: int) -> None:
        if not get_settings().discord_webhook:
            print("Webhook URL missing.")
            return

        message = {
            "content": (
                f"🚨 **Medication Alert:** Time to refill **{med_name}**! "
                f"You only have {days_left} days of stock remaining."
            ),
        }

        try:
            response = requests.post(get_settings().discord_webhook, json=message)
            response.raise_for_status()
            print(f"Alert sent successfully for {med_name}!")
        except Exception as e:
            print(f"Failed to send alert: {e}")


# Define default channels allows for mypy to check that any channel conforms to Protocol
DEFAULT_CHANNELS: tuple[NotificationChannel, ...] = (EmailChannel(), DiscordChannel())


# Function to trigger the alerts
def notify_low_stock(
    med_name: str, days_left: int, channels: Sequence[NotificationChannel] | None = None
) -> None:
    """Triggers every  notification channels for low-stock medication."""
    if channels is None:
        channels = DEFAULT_CHANNELS
    print(f"Triggering alerts for {med_name}...")
    for channel in channels:
        channel.send(med_name, days_left)
    print(f"Finished sending all alerts for {med_name}.")
