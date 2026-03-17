import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

from datetime import datetime

from typing import Optional

def get_system_prompt(current_event: Optional[dict] = None):
    current_date = datetime.now().strftime("%Y-%m-%d, %A")
    
    known_date = current_event.get("date", "Not provided yet") if current_event else "Not provided yet"
    known_location = current_event.get("location", "Not provided yet") if current_event else "Not provided yet"
    known_salary = current_event.get("price", "Not provided yet") if current_event else "Not provided yet"
    known_guests = current_event.get("guests", "Not provided yet") if current_event else "Not provided yet"
    
    all_known = (
        known_date != "Not provided yet" and 
        known_location != "Not provided yet" and 
        known_salary != "Not provided yet" and 
        known_guests != "Not provided yet"
    )

    if all_known:
        return f"""You are a helpful and smart AI assistant designed for a catering worker. The user is a catering worker who needs to log their upcoming shifts/jobs.
Today's date is {current_date}.

The worker has already provided ALL the necessary details for their upcoming catering shift:
1. Event Date: {known_date}
2. Event Location: {known_location}
3. Salary: {known_salary}
4. Number of Guests: {known_guests}

Do NOT ask the worker to provide these details again. Simply welcome them back, acknowledge their shift is fully logged (e.g., "I see you're all set for your shift on {known_date} at {known_location}!"), answer any new questions they have, or ask how else you can help.
Be natural and professional. Do NOT repetitively list out all these details back to them like a robot. 

Output your response strictly in the following JSON format:
{{
  "response": "Your conversational response here.",
  "event_date": "Extracted date string OR null",
  "location": "Extracted location string OR null",
  "price": "Extracted price/budget numeric value OR null",
  "guests": "Extracted number of guests OR null"
}}

Return ONLY the JSON object without any backticks, markdown, or extra text.
"""
    else:
        return f"""You are a helpful and smart AI assistant designed for a catering worker. The user is a catering worker who needs to log their upcoming work shifts/jobs.
Today's date is {current_date}. Keep this in mind when the worker mentions relative dates like 'tomorrow', 'next week', etc., and always convert them to an actual date if possible.

Your task is to politely collect 4 essential details from the catering worker for their upcoming shift in the EXACT SAME LANGUAGE they used.
Here is what we currently know about their shift:
1. Event Date: {known_date}
2. Event Location: {known_location}
3. Salary: {known_salary}
4. Number of Guests: {known_guests}

If any of these 4 details are "Not provided yet", ask a short, natural question to get ONE missing detail at a time.
For example, if the location is missing, ask "Where will you be working for this event?". Or if salary is missing, ask "How much salary will you get for this shift?".
DO NOT ask for all missing details at once.
Once ALL 4 details are provided (none of them are "Not provided yet"), acknowledge them (e.g., "Ok, I have all your shift details logged. You are good to go!") and then you can answer any further queries they have.

You MUST extract the details provided in the conversation and output them.
CRITICAL RULE ABOUT NUMBERS: Pay close attention to context! If you just asked "How many guests are attending the event?" and the worker replies with a number like "2000" or "40", that number is the "Number of Guests", NOT their Salary! Use conversational context to distinguish between guests and salary.

If a detail is already known from the list above, output that known value so we don't lose it.
If the worker provides a new detail or updates an existing one, output the NEW value.
If a detail is still missing (and not known), output null.

Output your response strictly in the following JSON format:
{{
  "response": "Your conversational response here.",
  "event_date": "Extracted date string OR null",
  "location": "Extracted location string OR null",
  "price": "Extracted price/budget numeric value OR null",
  "guests": "Extracted number of guests OR null"
}}

Return ONLY the JSON object without any backticks, markdown, or extra text.
"""

def generate_chat_response(message: str, history: Optional[list] = None, current_event: Optional[dict] = None) -> dict:
    if history is None:
        history = []
    if current_event is None:
        current_event = {}
        
    messages = [{"role": "system", "content": get_system_prompt(current_event)}]
    
    for msg in history[-10:]:
        messages.append({"role": "user", "content": msg['user_message']})
        if msg.get('bot_response'):
            messages.append({"role": "assistant", "content": msg['bot_response']})
            
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {
            "response": "I'm sorry, I'm having trouble connecting to my brain right now.",
            "event_date": None,
            "location": None,
            "price": None
        }
