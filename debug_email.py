from utils import generate_email_body, send_email_notification
from dotenv import load_dotenv
import os

# Explicitly load .env to be sure
load_dotenv()

print(f"DEBUG: Read SMTP_EMAIL from env: {os.getenv('SMTP_EMAIL')}")
# Mask password for safety in logs
pwd = os.getenv('SMTP_PASSWORD')
print(f"DEBUG: Read SMTP_PASSWORD available: {'Yes' if pwd else 'No'}")

# Test Data
requester = "TestUser"
item = "Dell Latitude 5420 (Laptop)"
qty = 2
purpose = "New hires in Engineering"

# Generate Body
body = generate_email_body(requester, item, qty, purpose)

print("----- Generated HTML Body -----")
# print(body[:100] + "...") # Truncate for cleaner log
print("-------------------------------")

# Test Sending
# Use the same email as sender for testing to ensure it works
to_email = os.getenv('SMTP_EMAIL') 
print(f"Testing sending email to: {to_email}")

success = send_email_notification(to_email, "Test Request Debug", body, is_html=True)

if success:
    print("Mock/Real verification completed successfully! Check your inbox.")
else:
    print("Failed to send email. Check error logs above.")
