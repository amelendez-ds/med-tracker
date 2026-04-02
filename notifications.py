import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_low_stock_alert(med_name: str, days_left: int):
    """Sends a real email alert if stock is low."""

    # Safety check: Don't crash if credentials aren't set
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print(
            f"Terminal Alert: {med_name} is low ({days_left} days). Email credentials missing."
        )
        return

    msg = EmailMessage()
    msg.set_content(
        f"Time to refill {med_name}! You only have {days_left} days of stock remaining."
    )
    msg["Subject"] = f"Medication Alert: Low stock for {med_name}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS  # Sending it to yourself

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 587) as smtp:
            # Connect to the server
            smtp.ehlo()  # Identify app to Google
            smtp.starttls()  # Secure connection
            smtp.ehlo()  # Reidentify now that it's secure
            # Login and send
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Alert email sent successfully for {med_name}!")
    except Exception as e:
        print(f"Failed to send email: {e}")
