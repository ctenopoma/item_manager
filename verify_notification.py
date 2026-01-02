import logging
# Mock smtplib
import sys
from unittest.mock import MagicMock
sys.modules['smtplib'] = MagicMock()

from inventory_app.database import SessionLocal
from inventory_app.models import NotificationSettings, EmailTemplate, Item, User, ItemStatus, Role
from inventory_app.notification import check_and_send_notifications
from datetime import date, timedelta

def test_notification():
    db = SessionLocal()
    
    # 1. Setup Settings
    settings = db.query(NotificationSettings).first()
    if not settings:
        settings = NotificationSettings(
            n_days_before=1,
            m_days_overdue=1,
            sender_email="test@example.com"
        )
        db.add(settings)
    else:
        # Update/Ensure values for test
        settings.n_days_before = 1
        settings.m_days_overdue = 1
        
    # 2. Setup Template
    template = db.query(EmailTemplate).filter(EmailTemplate.name == "reminder_before").first()
    if not template:
        template = EmailTemplate(
            name="reminder_before",
            subject="Reminder: {item_name} due soon",
            body="Hello {user_name}, please return {item_name} by {due_date}."
        )
        db.add(template)
    
    # 3. Setup User
    user = db.query(User).filter(User.email == "borrower@example.com").first()
    if not user:
        user = User(
            username="borrower",
            email="borrower@example.com",
            role=Role.user.value
        )
        db.add(user)
    db.commit()
    
    # Refresh to get IDs
    db.refresh(user)

    # 4. Setup Item (Due tomorrow -> N=1 day before)
    today = date.today()
    due_tomorrow = today + timedelta(days=1)
    
    item = Item(
        name="Test Item 123",
        management_code="TEST-123",
        status=ItemStatus.borrowed.value,
        owner_id=user.id,
        due_date=due_tomorrow
    )
    db.add(item)
    db.commit()
    
    print(f"Created item due on {due_tomorrow} (Tomorrow). Settings N={settings.n_days_before}.")
    
    # 5. Run Check
    print("Running check_and_send_notifications...")
    check_and_send_notifications(db)
    
    # 6. Verify (Check logs/output)
    # Since we mocked smtplib, we can't check actual email, but we rely on print statements in check_and_send_notifications
    
    # Cleanup
    db.delete(item)
    # Don't delete settings/templates as they might persist
    db.commit()
    db.close()

if __name__ == "__main__":
    test_notification()
