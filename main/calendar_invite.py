from ics import Calendar, Event
from datetime import datetime
import pytz
import uuid

# Function to generate a .ics (calendar invite) file
def generate_ics(start_str, end_str, meeting_url="https://zoom.us/my/smartmeeting"):
    """
    Generate a .ics calendar invite file for Smart AI Meeting.
    """

    # ✅ Remove extra spaces and " UTC" from start and end time strings
    start_str = start_str.strip().replace(" UTC", "")
    end_str = end_str.strip().replace(" UTC", "")

    # ✅ Convert the cleaned time strings into datetime objects in UTC timezone
    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.utc)
    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.utc)

    # 📌 Create a calendar event
    event = Event()
    event.uid = str(uuid.uuid4())  # Generate a unique ID for the event
    event.name = "🤖 Smart AI Meeting"  # Title of the meeting
    event.begin = start_dt  # Event start time
    event.end = end_dt  # Event end time
    event.location = meeting_url  # Location or meeting link
    event.description = f"""Zoom Meeting Link: {meeting_url}
    
Please join the meeting on time from any device."""  # Event description

    # 📆 Create a new calendar and add the event
    cal = Calendar()
    cal.events.add(event)

    # 💾 Save the calendar with event into a file named 'meeting.ics'
    file_path = "meeting.ics"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())

    # Return the file path for further use (like email attachment)
    return file_path
