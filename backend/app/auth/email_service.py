import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load from .env via FastAPI's startup (dotenv already loaded in config)
EMAIL_HOST = os.getenv("EMAIL_HOST", "mailhog")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 1025))
EMAIL_FROM = os.getenv("EMAIL_FROM", "no-reply@easyabroad.local")

# URL of your front end (should include protocol & host, no trailing slash)
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:8080")

def send_reset_email(recipient_email: str, reset_token: str):
    # ← Here’s the updated reset_link
    reset_link = f"{FRONTEND_BASE_URL}/reset-password.html?token={reset_token}"

    subject = "Reset Your Password – EasyAbroad"
    html_body = f"""
    <html>
      <body>
        <p>Hello,</p>
        <p>You (or someone using this email) requested a password reset on EasyAbroad.</p>
        <p><a href="{reset_link}">Click here to choose a new password</a></p>
        <p>This link is valid for 1 hour. If you did not request a password reset, you can safely ignore this.</p>
        <p>Best,<br>The EasyAbroad Team</p>
      </body>
    </html>
    """

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_body, "html"))

    # Send via MailHog (no auth needed)
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.sendmail(EMAIL_FROM, recipient_email, msg.as_string())


