import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import Item, NotificationSettings, EmailTemplate, ItemStatus, User

def send_email(settings: NotificationSettings, to_email: str, subject: str, body: str):
    if not settings.sender_email or not settings.smtp_server:
        print("SMTP settings not configured.")
        return

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_and_send_notifications(db: Session):
    print("Checking for notifications...")
    settings = db.query(NotificationSettings).first()
    if not settings:
        print("No notification settings found.")
        return

    today = datetime.now().date()
    items = db.query(Item).filter(Item.status == ItemStatus.borrowed, Item.due_date != None).all()

    for item in items:
        if not item.owner or not item.owner.email:
            continue

        days_diff = (item.due_date - today).days
        template_name = None

        if days_diff == settings.n_days_before:
            template_name = "reminder_before"
        elif days_diff == 0:
            template_name = "due_date"
        elif days_diff < 0 and (-days_diff) % settings.m_days_overdue == 0:
            template_name = "overdue"

        if template_name:
            template = db.query(EmailTemplate).filter(EmailTemplate.name == template_name).first()
            if template:
                subject = template.subject
                body = template.body.format(
                    user_name=item.owner.display_name or item.owner.username,
                    item_name=item.name,
                    due_date=item.due_date,
                    days_overdue=-days_diff if days_diff < 0 else 0
                )
                print(f"Sending {template_name} email to {item.owner.email}")
                send_email(settings, item.owner.email, subject, body)
