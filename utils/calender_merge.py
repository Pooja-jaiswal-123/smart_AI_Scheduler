import json
from datetime import datetime

# ⏳ Helper function to convert "HH:MM" string to datetime object
def parse_time(slot):
    return datetime.strptime(slot, "%H:%M")

# 🔄 Finds overlapping time ranges between two users' slots
def find_overlap(slots1, slots2):
    overlap = []
    for a in slots1:
        for b in slots2:
            # Get latest start time and earliest end time
            start = max(parse_time(a["start"]), parse_time(b["start"]))
            end = min(parse_time(a["end"]), parse_time(b["end"]))

            # Only if valid overlap (i.e., time duration > 0)
            if start < end:
                overlap.append({
                    "start": start.strftime("%H:%M"),
                    "end": end.strftime("%H:%M")
                })
    return overlap

# 🔍 Loop through all users and find the common overlapping slots
def find_common_slots(calendars):
    users = list(calendars.keys())  # Extract all usernames from JSON
    common_slots = calendars[users[0]]  # Start with the first user's slots

    # Compare with each subsequent user's calendar
    for user in users[1:]:
        common_slots = find_overlap(common_slots, calendars[user])
        if not common_slots:
            break  # If no overlap remains, exit early
    return common_slots

# 🚀 Run this part only if the script is executed directly
if __name__ == "__main__":
    # 📂 Ask user to provide path to JSON file
    file_path = input("📁 Enter the path of the JSON calendar file: ")

    try:
        # 📖 Read and parse calendar file
        with open(file_path, "r") as f:
            calendars = json.load(f)

        # ✅ Find common meeting slots
        common = find_common_slots(calendars)

        if common:
            print(f"✅ Common Slots Found: {common}")
        else:
            print("❌ No common slots found.\n📩 Suggestion: Reschedule to a better time.")

    except Exception as e:
        # ⚠️ Handle file read or parsing errors
        print(f"⚠️ Error: {str(e)}")
