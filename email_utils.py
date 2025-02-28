import os
import smtplib
import uuid
from dotenv import load_dotenv  # <-- import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from gmail_service import get_gmail_service, create_message, send_message

load_dotenv()  # load variables from .env file
public_url = "https://35e0-103-228-147-209.ngrok-free.app"  # Add your current URL
os.environ["PUBLIC_URL"] = public_url
print(f"Manually set PUBLIC_URL: {public_url}")

def generate_token():
    """Generates a unique token."""
    return str(uuid.uuid4())

def send_email(recipient, subject, message_text):
    """
    Sends an email using the Gmail API.
    
    This version uses OAuth2 via credentials.json and token.json (managed in gmail_service.py)
    to authenticate with Gmail.
    """
    try:
        service = get_gmail_service()
        # Define the sender. This should match the authenticated account.
        sender = "pracmystic2562@gmail.com"  # Set your Gmail address here.
        # Create the email message.
        msg = create_message(sender, recipient, subject, message_text)
        # Send the message using Gmail API.
        send_message(service, "me", msg)
    except Exception as e:
        raise Exception(f"Failed to send email using Gmail API: {e}")

# Example usage in your registration code would be:
# try:
#     token = generate_token()
#     verification_link = f"http://localhost:5000/verify?token={token}"
#     email_subject = "Please verify your email address"
#     email_body = f"Click the link below to verify your email:\n{verification_link}"
#     send_email(user_email, email_subject, email_body)
# except Exception as e:
#     self.show_error("Failed to send verification email")
#     handle_error(e)