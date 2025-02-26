import smtplib
import requests
from utils.config import OPENAI_API_KEY

def send_alert(subject, message, recipient_email):
    """ Sends an email alert for stock/crypto breakout conditions. """
    sender_email = "??"
    sender_password = "??"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(sender_email, recipient_email, email_message)

def check_alert_conditions(asset, price, volume, moving_avg):
    """ Checks if the asset has met breakout conditions for alerting. """
    if price > moving_avg * 1.05 and volume > 1.5 * moving_avg:
        send_alert(f"🔥 {asset} Breakout Alert!",
                   f"{asset} has broken out with price {price} and high volume!",
                   "recipient@example.com")


