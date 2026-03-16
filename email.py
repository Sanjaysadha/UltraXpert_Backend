import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings

def send_otp_email(email_to: str, otp: str):
    """
    Sends an OTP email for password reset.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("DEBUG: SMTP credentials not set. OTP would be:", otp)
        return

    message = MIMEMultipart()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to
    message["Subject"] = "UltraXpert - Password Reset OTP"

    body = f"""
    Hello,

    You recently requested to reset your password for your UltraXpert account.
    Your One-Time Password (OTP) is:

    {otp}

    This OTP will expire in 10 minutes.

    If you did not request a password reset, please ignore this email.

    Best regards,
    The UltraXpert Team
    """
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
        print(f"DEBUG: OTP email sent to {email_to}")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        raise e
