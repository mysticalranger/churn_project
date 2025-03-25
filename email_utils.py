import os
import smtplib
import uuid
from dotenv import load_dotenv  # <-- import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from gmail_service import get_gmail_service, create_message, send_message
import secrets
import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()  # load variables from .env file
public_url = "https://0878-103-228-147-209.ngrok-free.app"  # Add your current URL
os.environ["PUBLIC_URL"] = public_url
print(f"Manually set PUBLIC_URL: {public_url}")

def generate_token(length=32):
    """Generate a secure random token for verification/reset."""
    return secrets.token_urlsafe(length)

def send_email(to_email, subject, body_text):
    """Send an email using Gmail API."""
    print(f"Attempting to send email to {to_email}")
    
    # Try a simpler approach using SMTP for testing
    try:
        # Your Gmail credentials
        gmail_user = 'your_email@gmail.com'  # Replace with your actual email
        gmail_password = 'your_app_password'  # Replace with your app password
        
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body_text, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email} via SMTP")
        return True
    except Exception as e:
        print(f"SMTP email sending failed: {str(e)}")
        
        # Fall back to Gmail API if SMTP fails
        try:
            print("Attempting to use Gmail API as fallback")
            # Gmail API credentials
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']
            creds = None
            
            # Check if token.json exists (contains user access tokens)
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                
            # If credentials don't exist or are invalid, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save credentials for next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                    
            # Create Gmail API service
            service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            message = MIMEText(body_text)
            message['to'] = to_email
            message['subject'] = subject
            
            # Encode the message for the Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully to {to_email} via Gmail API")
            return True
        except Exception as api_error:
            print(f"Gmail API error: {str(api_error)}")
            raise  # Re-raise the exception to be caught by the caller

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