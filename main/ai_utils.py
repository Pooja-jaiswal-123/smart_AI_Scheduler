# Import necessary modules
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Gemini API using the API key from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create a model object using the correct Gemini model name
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")


# Function to generate a confirmation email for a meeting
def generate_ai_message(name, slot, meeting_link):
    date = slot['start'].split()[0]
    start_time = slot['start'].split()[1]
    end_time = slot['end'].split()[1]

    prompt = f"""
Generate a short, friendly email for a meeting confirmation with the following details:
- Recipient name: {name}
- Date: {date}
- Time: {start_time} to {end_time} UTC
- Meeting link: {meeting_link}

Make it polite, professional, and natural. Avoid mentioning that it is AI-generated. End with a positive note.
"""

    try:
        print(f"🧠 Gemini called: Generating confirmation email for {name}...")
        response = model.generate_content(prompt)
        print("✅ Gemini email generation complete.")
        return response.text.strip()
    except Exception as e:
        print("❌ AI generation failed:", e)
        return None


# Function to choose the best time slot from a list using Gemini AI
def rank_slots_with_gpt(slots):
    if not slots:
        print("⚠️ No slots to rank.")
        return []

    slot_text = "\n".join(
        f"{i+1}. {slot['start']} to {slot['end']} UTC" for i, slot in enumerate(slots)
    )

    prompt = f"""
You are an intelligent scheduling assistant. Here are some available meeting slots:

{slot_text}

Choose the best slot based on:
- Natural working hours
- Balance for global time zones
- Ideal start times

Respond with only the slot number (e.g., 1, 2, etc.) of the best slot.
"""

    try:
        print("🧠 Gemini called: Ranking slots...")
        response = model.generate_content(prompt)
        content = response.text.strip()
        slot_number = int("".join(filter(str.isdigit, content)))
        print("✅ Gemini selected slot:", slot_number)
        return [slots[slot_number - 1]]
    except Exception as e:
        print("❌ Slot ranking failed:", e)
        return slots


# Function to create a reschedule email if no common slot is found
def generate_reschedule_message(name, sender, fallback_slots):
    if not fallback_slots:
        print("⚠️ No fallback slots provided for reschedule message.")
        return None

    slot_text = "\n".join(
        [f"- {slot['start']} to {slot['end']} UTC" for slot in fallback_slots]
    )

    prompt = f"""
You are a professional meeting assistant.

Write a polite reschedule email to {name}, saying that no common slot was found for the meeting.
Suggest the following time options for rescheduling:

{slot_text}

End the email kindly and professionally, signed by {sender}. Avoid mentioning this is AI-generated.
"""

    try:
        print(f"🧠 Gemini called: Generating reschedule email for {name}...")
        response = model.generate_content(prompt)
        print("✅ Reschedule email generation complete.")
        return response.text.strip()
    except Exception as e:
        print("❌ AI reschedule message generation failed:", e)
        return None
