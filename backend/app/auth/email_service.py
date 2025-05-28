# backend/app/auth/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

# Pull values from our Pydantic settings
EMAIL_HOST         = settings.EMAIL_HOST
EMAIL_PORT         = settings.EMAIL_PORT
EMAIL_FROM         = settings.EMAIL_FROM
FRONTEND_BASE_URL  = settings.FRONTEND_BASE_URL

def send_reset_email(recipient_email: str, reset_token: str):
    # Build the reset link using the frontend base URL
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

    # Build the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_body, "html"))

    # Send via SMTP (e.g. MailHog)
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.sendmail(EMAIL_FROM, recipient_email, msg.as_string())
