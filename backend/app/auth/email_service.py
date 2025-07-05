# backend/app/auth/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

EMAIL_HOST        = settings.EMAIL_HOST
EMAIL_PORT        = int(settings.EMAIL_PORT)
EMAIL_FROM        = settings.EMAIL_FROM
EMAIL_USER        = settings.EMAIL_USER
EMAIL_PASSWORD    = settings.EMAIL_PASSWORD
FRONTEND_BASE_URL = settings.FRONTEND_BASE_URL

def send_reset_email(recipient_email: str, reset_token: str, user_name: str = None):
    reset_link = f"{FRONTEND_BASE_URL}/reset-password.html?token={reset_token}"
    greeting = f"Hello {user_name}," if user_name else "Hello,"
    subject = "Reset Your Easy Abroad Password"
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Easy Abroad - Password Reset</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
    <div style="text-align: center; margin-bottom: 30px;">
      <img src="https://easyabroad.com/frontend/images/favicon.png" alt="Easy Abroad Logo" style="max-height: 50px;">
    </div>
    <h2 style="color: #333;">Reset Your Password</h2>
    <p>{greeting}</p>
    <p>We received a request to reset the password for your Easy Abroad account.</p>
    <p style="text-align: center; margin: 30px 0;">
      <a href="{reset_link}" style="background-color: #d62d81; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
    </p>
    <p>This link is valid for 1 hour. If you didn’t request a password reset, you can safely ignore this email.</p>
    <p>Best regards,<br><strong>The Easy Abroad Team</strong></p>
    <hr style="margin: 40px 0;">
    <p style="font-size: 12px; color: #999; text-align: center;">
      &copy; 2025 Easy Abroad. All rights reserved.<br>
      <a href="http://www.easy-abroad.de" style="color: #999;">www.easyabroad.com</a>
    </p>
  </div>
</body>
</html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()  # Enable TLS
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_FROM, recipient_email, msg.as_string())
    except Exception as e:
        print(f"⚠️ Failed to send reset email to {recipient_email}: {e}")