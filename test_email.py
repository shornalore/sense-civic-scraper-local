# create test_email.py
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email():
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    print(f"Testing email configuration...")
    print(f"Sender: {sender_email}")
    print(f"Recipient: {recipient_email}")
    print(f"Password length: {len(sender_password) if sender_password else 0}")
    
    if not all([sender_email, sender_password, recipient_email]):
        print("❌ Missing email configuration!")
        return False
    
    try:
        # Create test message
        msg = MIMEText("Test email from Civic Sense Scraper - Configuration successful!")
        msg['Subject'] = "🧪 Civic Sense Scraper - Email Test"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Connect and send
        print("📧 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Attempting authentication...")
        server.login(sender_email, sender_password)
        
        print("📤 Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email test successful! Check your inbox.")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("🔧 Solutions:")
        print("   1. Verify App-Specific Password (16 characters, no spaces)")
        print("   2. Ensure 2-Factor Authentication is enabled")
        print("   3. Check email address spelling")
        return False
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

if __name__ == "__main__":
    test_email()
