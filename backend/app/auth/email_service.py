import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")  # DAS FEHLTE!

def send_reset_email(recipient_email, reset_token):
    reset_link = f"{FRONTEND_BASE_URL}/visitor/V5_Reset_Password.html?token={reset_token}"
    subject = "Reset Your Password - EasyAbroad"
    body = f"""
    <p>Hello,</p>
    <p>You requested a password reset. Click the link below to choose a new password:</p>
    <p><a href="{reset_link}">Reset your password</a></p>
    <p>This link is valid for one hour. If you did not request this, please ignore it.</p>
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        # Kein TLS/LOGIN bei Mailhog nötig – ggf. Zeilen auskommentieren!
        # server.starttls()
        # server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, recipient_email, msg.as_string())
