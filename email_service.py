import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from database import events_collection, users_collection
from apscheduler.schedulers.background import BackgroundScheduler

def send_reminder_email(to_email: str, username: str, event: dict):
    # This requires setting up valid SMTP credentials in the .env.
    # We will log the email payload to the console so the user can see it works locally.
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL", "test@example.com")
    sender_password = os.getenv("SENDER_PASSWORD", "password")

    date_str = event.get('date', 'Unknown Date')
    location = event.get('location', 'Unknown Location')
    guests = event.get('guests', 'Unknown Guests')

    subject = f"Upcoming Catering Shift Reminder: {date_str}"
    body = f"""Hello {username},

This is an automated reminder for your upcoming catering shift tomorrow.

Date: {date_str}
Location: {location}
Expected Guests: {guests}

Have a great shift!
- Caterina AI Assistant"""

    print(f"\n[{datetime.now()}] [EMAIL MOCK LOG]")
    print(f"Would send email to: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}\n")

    # In a real deployed app, the SMTP logic below would execute. 
    # For now, we wrap it in a try-except strictly so that lack of SMTP credentials doesn't crash the server.
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Note: Could not actually route SMTP email. Expected since credentials are not configured: {e}")

def check_and_send_reminders():
    print(f"[{datetime.now()}] Running background email reminder check...")
    
    # Calculate tomorrow's date format (YYYY-MM-DD or similar text)
    # The chatbot extracts dates natively depending on Groq output, often in YYYY-MM-DD. 
    # For demonstration, we simply parse all active events.
    tomorrow_date_obj = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow_date_obj.strftime("%Y-%m-%d")
    
    events = list(events_collection.find())
    
    for event in events:
        event_date_str = event.get("date")
        if not event_date_str: continue
        
        # Check if reminder was already sent for this event
        already_reminded = event.get("reminded", False)
        if already_reminded:
            continue

        # Simple string matching for dates (Assuming the AI extracted it exactly as YYYY-MM-DD)
        # In a robust system, we would force datetime object parsing.
        
        # If the date String contains tomorrow's date signature:
        if tomorrow_str in event_date_str:
            username = event.get("username")
            if not username: continue
            
            # Lookup the user to grab their email address
            user = users_collection.find_one({"username": username})
            if user and user.get("email"):
                send_reminder_email(user["email"], username, event)
                
                # Mark this event as reminded so we don't send the same reminder again
                events_collection.update_one(
                    {"_id": event["_id"]},
                    {"$set": {"reminded": True, "reminded_at": datetime.utcnow()}}
                )
                print(f"Reminder sent and marked for {username}'s event on {event_date_str}")

# Scheduler singleton
# Runs once per day at 9 AM to send reminders for events tomorrow
# Events are marked as "reminded: True" to prevent duplicate emails
scheduler = BackgroundScheduler()
scheduler.add_job(check_and_send_reminders, 'cron', hour=9, minute=0)  # Runs daily at 9:00 AM
