import smtplib
from email.mime.text import MIMEText
from app.core.celery_app import celery_app
from app.core.config import settings


@celery_app.task
def send_registration_email(email: str, token: str) -> None:
    verification_url = f"http://localhost:8000/auth/verify/{token}"
    msg = MIMEText(f"Для підтвердження email перейди за посиланням: {verification_url}")
    msg["Subject"] = "Підтвердження реєстрації"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, email, msg.as_string())
