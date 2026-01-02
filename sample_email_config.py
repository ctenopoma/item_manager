import smtplib
from email.mime.text import MIMEText
import sys
from inventory_app.database import SessionLocal
from inventory_app.models import NotificationSettings

def check_email_settings():
    print("=== Email Settings Verification (Using DB Settings) ===")
    
    # --- Fetch Settings from DB ---
    db = SessionLocal()
    settings = db.query(NotificationSettings).first()
    db.close()

    default_smtp_server = "smtp.gmail.com"
    default_smtp_port = 587
    default_smtp_username = ""
    default_smtp_password = ""
    default_sender_email = ""

    if settings:
        print("Found settings in database.")
        default_smtp_server = settings.smtp_server or default_smtp_server
        default_smtp_port = settings.smtp_port or default_smtp_port
        default_smtp_username = settings.smtp_username or ""
        default_smtp_password = settings.smtp_password or ""
        default_sender_email = settings.sender_email or ""
    else:
        print("No settings found in database. Using hardcoded defaults.")

    default_receiver_email = "target@example.com"
    
    print("\nPlease confirm or update the settings below.")
    print("Press Enter to use the value in brackets [] (fetched from DB).")

    # Input Override
    smtp_server = input(f"SMTP Server [{default_smtp_server}]: ").strip() or default_smtp_server
    smtp_port_str = input(f"SMTP Port [{default_smtp_port}]: ").strip() or str(default_smtp_port)
    smtp_port = int(smtp_port_str)
    
    smtp_username = input(f"SMTP Username [{default_smtp_username}]: ").strip() or default_smtp_username
    
    # Hide password if it exists
    pass_display = "****" if default_smtp_password else "None"
    smtp_password = input(f"SMTP Password [{pass_display}]: ").strip() or default_smtp_password
    
    sender_email = input(f"Sender Email [{default_sender_email}]: ").strip() or default_sender_email
    receiver_email = input(f"Receiver Email [{default_receiver_email}]: ").strip() or default_receiver_email

    print("\nAttempting to send email...")
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"User: {smtp_username}")
    print(f"From: {sender_email} -> To: {receiver_email}")

    subject = "Test Email from Item Manager (Sample)"
    body = """
    Hello,
    
    This is a test email to verify the SMTP settings.
    If you are reading this, the configuration is correct.
    
    Regards,
    Item Manager Test Script
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1) # Show SMTP communication details
            server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print("\n[SUCCESS] Email sent successfully.")
    except Exception as e:
        print(f"\n[ERROR] Failed to send email: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    check_email_settings()
