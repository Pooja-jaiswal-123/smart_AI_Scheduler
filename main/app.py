from flask import Flask, render_template, request
from datetime import datetime
from send_email import send_email
from dateutil import parser
import pytz
import json
import re
import os
from calendar_invite import generate_ics
from zoom_meeting import create_zoom_meeting
from ai_utils import generate_ai_message, generate_reschedule_message, rank_slots_with_gpt

app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)
app.config['UPLOAD_FOLDER'] = './'

def clean_name(raw_input):
    if not raw_input:
        return "User"
    cleaned = re.sub(r'\d+', '', raw_input)
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', cleaned)
    return cleaned.strip().title() or "User"

def parse_slot(slot, timezone_str='Asia/Kolkata'):
    try:
        tz = pytz.timezone(timezone_str)
        start = parser.parse(slot['start'])
        end = parser.parse(slot['end'])
        if start.tzinfo is None:
            start = tz.localize(start)
        if end.tzinfo is None:
            end = tz.localize(end)
        return {
            "start": start.astimezone(pytz.utc),
            "end": end.astimezone(pytz.utc)
        }
    except Exception as e:
        print(f"Slot parse error: {e}")
        return None

def find_common_slots(users):
    common_slots = users[0]
    for i in range(1, len(users)):
        next_user = users[i]
        temp_common = []
        for slot1 in common_slots:
            for slot2 in next_user:
                if not slot1 or not slot2:
                    continue
                start = max(slot1['start'], slot2['start'])
                end = min(slot1['end'], slot2['end'])
                if start < end:
                    temp_common.append({"start": start, "end": end})
        common_slots = temp_common
    return [{
        "start": s["start"].strftime("%Y-%m-%d %H:%M"),
        "end": s["end"].strftime("%Y-%m-%d %H:%M")
    } for s in common_slots]

class UserAgent:
    def __init__(self, name, email, slots, timezone='Asia/Kolkata'):
        self.name = name if name and name.strip() else "User"
        self.email = email
        self.slots = slots
        self.timezone = timezone

    def propose_slot(self, other_agents):
        all_slots = [self.slots] + [agent.slots for agent in other_agents]
        common_slots = find_common_slots(all_slots)
        print("👉 Found Common Slots:", common_slots)
        return rank_slots_with_gpt(common_slots)[0] if common_slots else None

    def generate_message(self, slot, meeting_link, custom_message=None):
        if custom_message:
            return f"""Dear {self.name},\n\n{custom_message}\n\n🔗 Meeting Link: {meeting_link}"""

        try:
            print(f"🧠 Gemini called: Generating confirmation email for {self.name}...")
            ai_msg = generate_ai_message(self.name, slot, meeting_link)
            if ai_msg:
                print("✅ Gemini email generation complete.")
                return ai_msg
        except Exception as e:
            print("AI message generation failed:", e)

        dt_start = parser.parse(slot['start'])
        dt_end = parser.parse(slot['end'])

        utc_start = dt_start.strftime('%I:%M %p')
        utc_end = dt_end.strftime('%I:%M %p')
        date = dt_start.strftime('%Y-%m-%d')

        ist = pytz.timezone('Asia/Kolkata')
        ist_start = dt_start.astimezone(ist).strftime('%I:%M %p')
        ist_end = dt_end.astimezone(ist).strftime('%I:%M %p')

        try:
            local_tz = pytz.timezone(self.timezone)
        except:
            local_tz = pytz.utc
        local_start = dt_start.astimezone(local_tz).strftime('%I:%M %p')
        local_end = dt_end.astimezone(local_tz).strftime('%I:%M %p')
        local_label = self.timezone

        return f"""
Dear {self.name},

I hope you're doing well.

We've successfully scheduled a meeting based on mutual availability:

📅 Date: {date}

🕒 Meeting Time:
- UTC: {utc_start} to {utc_end}
- IST (India): {ist_start} to {ist_end}
- Your Time ({local_label}): {local_start} to {local_end}

🔗 Meeting Link: {meeting_link}
📌 Calendar Invite: Please find the attached .ics file to add this meeting to your calendar.

Looking forward to your presence.

Best regards,  
Smart Scheduler Team
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        sender_name = request.form.get('sender_name', 'Smart Scheduler')
        custom_link = request.form.get('custom_link')
        custom_message = request.form.get('custom_message')
        confirm = request.form.get('confirm_choice')

        file = request.files.get('calendar_file')
        start_times = request.form.getlist('start_times[]')
        end_times = request.form.getlist('end_times[]')
        manual_emails = request.form.getlist('manual_emails[]')
        timezones = request.form.getlist('timezones[]')

        all_users_slots = []
        agents = []

        if file and file.filename != '':
            try:
                data = json.load(file)
                for _, user_data in data.items():
                    slots = user_data.get("slots")
                    email = user_data.get("email")
                    tz = user_data.get("timezone", 'Asia/Kolkata')
                    raw_name = user_data.get("name") or (email.split('@')[0] if email else "")
                    name = clean_name(raw_name)

                    if slots:
                        parsed_slots = [parse_slot(slot, tz) for slot in slots if slot]
                        all_users_slots.append(parsed_slots)
                        agents.append(UserAgent(name, email, parsed_slots, tz))
            except Exception as e:
                result = f"<div class='text-red-600 font-semibold'>⚠️ Invalid JSON file: {e}</div>"
                return render_template('index.html', result=result)

        for start, end, email, tz in zip(start_times, end_times, manual_emails, timezones):
            if start and end and email:
                parsed = parse_slot({"start": start.strip(), "end": end.strip()}, tz)
                if parsed:
                    parsed_slots = [parsed]
                    raw_name = email.split('@')[0] if '@' in email else 'User'
                    name = clean_name(raw_name)
                    all_users_slots.append(parsed_slots)
                    agents.append(UserAgent(name, email.strip(), parsed_slots, tz))

        if len(agents) < 2:
            return render_template('index.html', result="❌ Please provide time slots for at least 2 users.")

        top_slot = agents[0].propose_slot(agents[1:])

        if top_slot:
            if confirm == 'ask':
                dt_start = parser.parse(top_slot['start'])
                dt_end = parser.parse(top_slot['end'])

                ist = pytz.timezone('Asia/Kolkata')
                ist_start = dt_start.astimezone(ist).strftime('%I:%M %p')
                ist_end = dt_end.astimezone(ist).strftime('%I:%M %p')
                utc_start = dt_start.strftime('%I:%M %p')
                utc_end = dt_end.strftime('%I:%M %p')
                meeting_date = dt_start.astimezone(ist).strftime('%Y-%m-%d')

                return render_template(
                    'confirm.html',
                    slot=top_slot,
                    agents=agents,
                    custom_link=custom_link,
                    custom_message=custom_message,
                    sender_name=sender_name,
                    ist_start=ist_start,
                    ist_end=ist_end,
                    utc_start=utc_start,
                    utc_end=utc_end,
                    meeting_date=meeting_date
                )

            meeting_link = custom_link or create_zoom_meeting(
                start_time=top_slot['start'],
                topic="AI Scheduled Meeting",
                duration=30
            )

            for agent in agents:
                msg_text = agent.generate_message(top_slot, meeting_link, custom_message)
                ics_file = generate_ics(top_slot['start'], top_slot['end'], meeting_link)
                try:
                    send_email(
                        to_email=agent.email,
                        subject=f"Meeting Confirmation – Scheduled by {sender_name}",
                        body_text=msg_text,
                        ics_path=ics_file
                    )
                except Exception as e:
                    result += f"<br>⚠️ Email failed to send to {agent.email}: {e}"

            result = f"""
            <div class="result-box">
                <strong>✅ Meeting Scheduled Successfully</strong><br><br>
                <strong>🗓️ Date:</strong> {top_slot['start'].split()[0]}<br>
                <strong>🕒 Time:</strong> {top_slot['start'].split()[1]} to {top_slot['end'].split()[1]} UTC<br><br>
                Invitation emails have been sent to all participants.
            </div>
            """
        else:
            fallback_slots = find_common_slots(all_users_slots)[:3]
            print("🌀 Fallback Slots:", fallback_slots)

            result = """
            ❌ No common slots found.<br>
            A polite reschedule request has been emailed to participants.
            """
            for agent in agents:
                print(f"🧠 Gemini called: Generating reschedule email for {agent.name}...")
                msg_text = generate_reschedule_message(agent.name, sender_name, fallback_slots)
                if msg_text:
                    print("✅ Gemini reschedule email done.")
                else:
                    print("⚠️ Gemini reschedule message failed, using fallback message.")

                if not msg_text:
                    msg_text = f"""Dear {agent.name},

Unfortunately, no mutual meeting slot was found.

Kindly review your availability and suggest alternate time slots.

Regards,  
{sender_name}
"""
                try:
                    send_email(
                        to_email=agent.email,
                        subject=f"Meeting Reschedule Request – From {sender_name}",
                        body_text=msg_text
                    )
                except Exception as e:
                    result += f"<br>⚠️ Email failed to send to {agent.email}: {e}"

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
