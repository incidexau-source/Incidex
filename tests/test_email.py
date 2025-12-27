"""
Test Email Credentials
Verifies that the provided email credentials work with Gmail SMTP.
"""

import smtplib
import os

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

def verify_email():
    print(f"Testing connection to {EMAIL_HOST}:{EMAIL_PORT}...")
    try:
        server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
        print("Connected. Logging in...")
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        print("Login SUCCESSFUL.")
        server.quit()
        print("Email credentials are valid.")
    except Exception as e:
        print(f"Login FAILED: {e}")

if __name__ == "__main__":
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("Error: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set.")
    else:
        verify_email()
