from datetime import datetime

# This function converts a string time like "14:30" into a datetime object
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# This function finds overlapping time slots between two users
def find_overlap(slots1, slots2):
    overlap = []
    for a in slots1:
        for b in slots2:
            # Get the latest start time and the earliest end time
            start = max(parse_time(a['start']), parse_time(b['start']))
            end = min(parse_time(a['end']), parse_time(b['end']))

            # If the start time is before the end time, it's a valid overlap
            if start < end:
                overlap.append({
                    'start': start.strftime("%H:%M"),  # Convert back to string format
                    'end': end.strftime("%H:%M")
                })
    return overlap

# This function takes a list of calendars (one per user) and finds time slots common to all users
def find_common_slots(calendars):
    common = calendars[0]  # Start with the first user's slots
    for cal in calendars[1:]:  # Check overlap with each remaining user's slots
        common = find_overlap(common, cal)  # Update common slots
        if not common:
            break  # If no overlap found at any step, stop early
    return common
