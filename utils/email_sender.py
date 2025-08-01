"""
Email functionality for sending scraper reports
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import Config

class EmailSender:
    """Email sender for scraper reports"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('civic_scraper')
        
        # Debug email configuration on initialization
        self.debug_email_config()
    
    def debug_email_config(self):
        """Debug email configuration"""
        print("\n📧 EmailSender Configuration Debug:")
        print(f"SENDER_EMAIL: {self.config.SENDER_EMAIL or 'NOT SET'}")
        print(f"RECIPIENT_EMAIL: {self.config.RECIPIENT_EMAIL or 'NOT SET'}")
        print(f"SENDER_PASSWORD: {'SET (' + str(len(self.config.SENDER_PASSWORD)) + ' chars)' if self.config.SENDER_PASSWORD else 'NOT SET'}")
        print(f"SMTP Server: {self.config.SMTP_SERVER}")
        print(f"SMTP Port: {self.config.SMTP_PORT}")
        
        # Check configuration validity
        if self.config.validate_email_config():
            print("✅ All email configuration is valid and ready")
        else:
            missing_fields = self.config.get_missing_email_fields()
            print(f"❌ Email configuration incomplete. Missing: {', '.join(missing_fields)}")
            print("\n🔧 To fix this issue:")
            print("1. Make sure your .env file exists in the project root")
            print("2. Check that .env file contains (no quotes, no spaces in password):")
            print("   SENDER_EMAIL=your.actual.email@gmail.com")
            print("   SENDER_PASSWORD=your16charapppassword")
            print("   RECIPIENT_EMAIL=your.personal@email.com")
            print("3. Ensure you're using Gmail App-Specific Password (16 characters)")
            print("4. Verify 2-Factor Authentication is enabled on Gmail")
        print("-" * 60)
    
    def validate_configuration(self):
        """Validate email configuration before sending"""
        missing_config = self.config.get_missing_email_fields()
        
        if missing_config:
            error_msg = f"❌ Email configuration incomplete. Missing: {', '.join(missing_config)}"
            error_msg += f"\n\n🔧 Please ensure your .env file contains:"
            error_msg += f"\nSENDER_EMAIL=your.actual.email@gmail.com"
            error_msg += f"\nSENDER_PASSWORD=your_16_char_app_password"
            error_msg += f"\nRECIPIENT_EMAIL=your.personal@email.com"
            error_msg += f"\n\n📋 Current values:"
            error_msg += f"\nSENDER_EMAIL: {self.config.SENDER_EMAIL or 'NOT SET'}"
            error_msg += f"\nSENDER_PASSWORD: {'SET (' + str(len(self.config.SENDER_PASSWORD)) + ' chars)' if self.config.SENDER_PASSWORD else 'NOT SET'}"
            error_msg += f"\nRECIPIENT_EMAIL: {self.config.RECIPIENT_EMAIL or 'NOT SET'}"
            error_msg += f"\n\n💡 Remember:"
            error_msg += f"\n• Use Gmail App-Specific Password (not regular password)"
            error_msg += f"\n• Remove all spaces from the 16-character password"
            error_msg += f"\n• Enable 2-Factor Authentication on Gmail"
            error_msg += f"\n• No quotes around values in .env file"
            raise Exception(error_msg)
    
    def send_reports(self, file_paths: List[str], post_count: int, duration: float, requests_made: int, 
                    duplicates_prevented: int = 0, content_filtered: int = 0):
        """Send generated reports via email with enhanced statistics"""
        
        # Validate configuration before attempting to send
        self.logger.info("🔍 Validating email configuration...")
        self.validate_configuration()
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.config.SENDER_EMAIL
        msg['To'] = self.config.RECIPIENT_EMAIL
        msg['Subject'] = f"🚗 Enhanced Civic Sense Report - {post_count} Unique Posts - {datetime.now().strftime('%Y-%m-%d %H:%M IST')}"
        
        # Enhanced email body
        success_rate = (post_count/(post_count+duplicates_prevented+content_filtered))*100 if (post_count+duplicates_prevented+content_filtered) > 0 else 0
        
        body = f"""
🚗 Enhanced Automated Civic Sense Scraping Report

📊 Session Summary:
• Duration: {duration:.1f} minutes
• Unique Posts Collected: {post_count}  
• Duplicates Prevented: {duplicates_prevented}
• Content Filtered: {content_filtered}
• Total Requests Made: {requests_made}
• Collection Success Rate: {success_rate:.1f}%
• Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}

📁 Attached Files ({len(file_paths)}):
{chr(10).join([f"• {os.path.basename(fp)}" for fp in file_paths])}

🔒 Quality Assurance:
• Zero duplicate URLs or content
• All posts contain required civic sense terms
• India-specific context verified
• Community engagement validated

🎯 Topics Covered:
• Civic Sense in India
• Road Rage Incidents  
• Bad Driving Behavior
• Traffic Violations
• Road Safety Discussions

🌐 Data Sources:
• r/india, r/bangalore, r/mumbai
• r/delhi, r/pune, r/chennai
• r/AskIndia, r/CarsIndia, r/indianbikes
• Reddit-wide searches for civic sense topics

📈 Report Types:
• Comprehensive Report: Detailed analysis with statistics and matched terms
• Links Collection: Unique URLs with metadata and topic classification
• Session Statistics: Performance metrics and quality insights

🤖 Enhanced Civic Sense Command Scraper v2.1
Next manual run: When you execute the script again

Happy analyzing! 📊✨

---
Email Configuration Used:
From: {self.config.SENDER_EMAIL}
To: {self.config.RECIPIENT_EMAIL}
SMTP: {self.config.SMTP_SERVER}:{self.config.SMTP_PORT}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach each file
        files_attached = 0
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    msg.attach(part)
                    files_attached += 1
                    self.logger.info(f"📎 Attached: {os.path.basename(file_path)}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to attach {file_path}: {e}")
        
        # Send email
        try:
            self.logger.info(f"📧 Connecting to {self.config.SMTP_SERVER}:{self.config.SMTP_PORT}")
            self.logger.info(f"📤 Sending from: {self.config.SENDER_EMAIL}")
            self.logger.info(f"📨 Sending to: {self.config.RECIPIENT_EMAIL}")
            
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            
            self.logger.info("🔐 Authenticating with Gmail...")
            server.login(self.config.SENDER_EMAIL, self.config.SENDER_PASSWORD)
            
            self.logger.info("📨 Sending email with attachments...")
            text = msg.as_string()
            server.sendmail(self.config.SENDER_EMAIL, self.config.RECIPIENT_EMAIL, text)
            server.quit()
            
            self.logger.info(f"✅ Email sent successfully to {self.config.RECIPIENT_EMAIL}")
            self.logger.info(f"📎 Files attached: {files_attached}/{len(file_paths)}")
            print(f"\n🎉 SUCCESS! Email with {files_attached} attachments sent to {self.config.RECIPIENT_EMAIL}")
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Gmail authentication failed: {e}"
            error_msg += f"\n\n🔧 Common solutions:"
            error_msg += f"\n1. Generate a new Gmail App-Specific Password"
            error_msg += f"\n2. Ensure 2-Factor Authentication is enabled"
            error_msg += f"\n3. Remove all spaces from the 16-character password"
            error_msg += f"\n4. Double-check email address spelling"
            error_msg += f"\n\n📋 Current configuration:"
            error_msg += f"\nEmail: {self.config.SENDER_EMAIL}"
            error_msg += f"\nPassword Length: {len(self.config.SENDER_PASSWORD)} characters"
            raise Exception(error_msg)
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"❌ Recipient email refused: {e}"
            error_msg += f"\n\n🔧 Check that recipient email is correct: {self.config.RECIPIENT_EMAIL}"
            raise Exception(error_msg)
            
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"❌ SMTP server disconnected: {e}"
            error_msg += f"\n\n🔧 Network connection issue. Please try again."
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"❌ Failed to send email: {e}"
            error_msg += f"\n\n📋 Email configuration used:"
            error_msg += f"\nFrom: {self.config.SENDER_EMAIL}"
            error_msg += f"\nTo: {self.config.RECIPIENT_EMAIL}"
            error_msg += f"\nSMTP: {self.config.SMTP_SERVER}:{self.config.SMTP_PORT}"
            raise Exception(error_msg)
    
    def test_email_connection(self):
        """Test email connection without sending a full report"""
        try:
            self.validate_configuration()
            
            # Test SMTP connection
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SENDER_EMAIL, self.config.SENDER_PASSWORD)
            server.quit()
            
            print("✅ Email connection test successful!")
            return True
            
        except Exception as e:
            print(f"❌ Email connection test failed: {e}")
            return False
