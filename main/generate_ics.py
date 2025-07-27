from ics import Calendar, Event
from datetime import datetime
import pytz
import uuid
import os

def generate_ics(start, end, link, title="AI Scheduled Meeting"):
    # Create calendar and event
    cal = Calendar()
    event = Event()

    # Ensure start and end are in correct ISO format
    if isinstance(start, str):
        start = datetime.fromisoformat(start)
    if isinstance(end, str):
        end = datetime.fromisoformat(end)

    # Force UTC timezone if not present
    if start.tzinfo is None:
        start = pytz.utc.localize(start)
    if end.tzinfo is None:
        end = pytz.utc.localize(end)

    # Set event details
    event.name = title
    event.begin = start
    event.end = end
    event.uid = str(uuid.uuid4())
    event.description = f"Zoom Meeting Link: {link}"
    event.location = link
    event.url = link

    # Add event to calendar
    cal.events.add(event)

    # Generate unique filename to avoid overwrite
    filename = f"meeting_{uuid.uuid4().hex}.ics"
    directory = "calendar_files"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

    # Save the .ics file
    with open(file_path, "w") as f:
        f.writelines(cal.serialize_iter())

    return file_path
