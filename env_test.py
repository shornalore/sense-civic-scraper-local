# create env_test.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🧪 Environment Variables Test:")
print(f"SENDER_EMAIL: {os.getenv('SENDER_EMAIL')}")
print(f"RECIPIENT_EMAIL: {os.getenv('RECIPIENT_EMAIL')}")
print(f"SENDER_PASSWORD: {'SET (' + str(len(os.getenv('SENDER_PASSWORD', ''))) + ' chars)' if os.getenv('SENDER_PASSWORD') else 'NOT SET'}")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'NOT SET')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'NOT SET')}")

# Test Config class
from config import Config
config = Config()
print("\n🔧 Config Class Test:")
print(f"Config.SENDER_EMAIL: {config.SENDER_EMAIL}")
print(f"Config.RECIPIENT_EMAIL: {config.RECIPIENT_EMAIL}")
print(f"Config.SENDER_PASSWORD: {'SET' if config.SENDER_PASSWORD else 'NOT SET'}")
