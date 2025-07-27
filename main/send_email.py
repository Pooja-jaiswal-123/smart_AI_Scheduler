import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ✅ Scope required to send emails using Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# 📍 Base path to root project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ Correct path to credentials and token inside 'credentials' folder
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'credentials', 'token.json')

def get_service():
    """
    Authenticate and return the Gmail API service.
    It checks for saved token or creates a new one if needed.
    """
    creds = None

    # 🔐 Load saved credentials if available
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 🔄 Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 💻 Run local server to authenticate with Google account
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 💾 Save the new token for next time
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    # 📧 Return Gmail API client
    return build('gmail', 'v1', credentials=creds)

def send_email(to_email, subject, body_text, ics_path=None):
    """
    Send an email using Gmail API with optional .ics calendar invite attached.
    """
    try:
        # ✅ Get authenticated Gmail API service
        service = get_service()

        # 📨 Create email container with mixed content (text + file)
        message = MIMEMultipart('mixed')
        message['To'] = to_email
        message['Subject'] = subject

        # 📄 Add plain text message to email
        message.attach(MIMEText(body_text, 'plain'))

        # 📅 If there's a .ics file, add it as inline and as attachment
        if ics_path and os.path.exists(ics_path):
            # 🔁 Read the .ics content
            with open(ics_path, 'r', encoding='utf-8') as f:
                ics_data = f.read()

            # 🧷 Inline calendar (so Google Calendar/Outlook detects it)
            calendar_part = MIMEText(ics_data, 'calendar', _charset='utf-8')
            calendar_part.add_header('Content-Type', 'text/calendar; method=REQUEST; charset=UTF-8')
            calendar_part.add_header('Content-Disposition', 'inline; filename="meeting.ics"')
            message.attach(calendar_part)

            # 📎 Attach .ics as downloadable file too
            with open(ics_path, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment; filename="meeting.ics"')
                message.attach(attachment)

        # 🚀 Encode and send the final email
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_body = {'raw': raw}
        result = service.users().messages().send(userId='me', body=send_body).execute()

        print(f"✅ Email sent to {to_email} — Message ID: {result['id']}")

    except Exception as e:
        print(f"⚠️ Failed to send email to {to_email}: {e}")
