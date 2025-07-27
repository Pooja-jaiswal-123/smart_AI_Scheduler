import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import base64

# 📂 Load credentials (Client ID, Secret, etc.) from .env file
load_dotenv()

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_USER_ID = os.getenv("ZOOM_USER_ID")

# 🔐 Generate Basic Auth Token by combining client_id and client_secret
def get_basic_auth_token():
    token = f"{CLIENT_ID}:{CLIENT_SECRET}"
    return base64.b64encode(token.encode()).decode()

# 🔑 Get Zoom OAuth access token using account credentials
def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    headers = {
        "Authorization": f"Basic {get_basic_auth_token()}",
    }
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        # ✅ Return access_token if request is successful
        return response.json().get("access_token")
    else:
        # ⚠️ Print error if token fetching fails
        print("⚠️ Access token error:", response.status_code, response.text)
        return None

# 📅 Create a Zoom meeting using the access token
def create_zoom_meeting(start_time, topic="AI Scheduled Meeting", duration=30):
    access_token = get_access_token()
    if not access_token:
        # 🔁 If access token fails, return default Zoom URL
        return "https://zoom.us/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # ⏰ Convert start_time string into datetime and format as UTC
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    payload = {
        "topic": topic,
        "type": 2,  # Type 2 = scheduled meeting
        "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Format to UTC ISO string
        "duration": duration,
        "timezone": "UTC",
        "settings": {
            "join_before_host": True,
            "waiting_room": False
        }
    }

    # 🌐 API endpoint to create meeting under specific Zoom user
    url = f"https://api.zoom.us/v2/users/{ZOOM_USER_ID}/meetings"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("✅ Zoom meeting created successfully!")
        return response.json()["join_url"]  # Return Zoom meeting link
    else:
        print("❌ Zoom meeting creation failed:", response.status_code, response.text)
        return "https://zoom.us/"  # Fallback Zoom homepage URL

# 🧪 Optional: Run this script directly to test meeting creation
if __name__ == "__main__":
    link = create_zoom_meeting("2025-07-06 14:30")
    print("🎯 Final Zoom Link:", link)
