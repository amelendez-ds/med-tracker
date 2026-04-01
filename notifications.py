import smtplib
from email.message import EmailMessage

# We replace this later
EMAIL_ADDRESS = "alvaromegu90@gmail.com"
EMAIL_PASSWORD = "my_email_password"


def send_low_stock_alert(med_name: str, days_left: int):
    """Calculates stock and sends an alert. Currently set to print to terminal for testing"""

    # 1. The immediate visual feedback for local testing
    print(
        f"\n ALARM TRIGGERED: {med_name} is running low! Only {days_left} days of stock remaining.\n"
    )

    # -- REAL EMAIL CODE (Uncomment later) ---
    # msg = EmailMessage()
    # msg.set_content(
    #     f"Time to refil {med_name}! You only have {days_left} days of stock remaining."
    # )
    # msg["Subject"] = f"Medication Alert: Low stock for {med_name}"
    # msg["From"] = EMAIL_ADDRESS
    # msg["To"] = EMAIL_ADDRESS  # Sending it to myself

    # try:
    #     with smtplib.SMTP_SLL("smtp.gmail.com", 465) as smtp:
    #         smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    #         smtp.send_message(msg)
    #     print("Real email sent successfully!")
    # except Exception as e:
    #     print(f"Failed to send real email: {e}")
