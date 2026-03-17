from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional, List
from datetime import datetime
from database import users_collection, chats_collection, events_collection
from chatbot import generate_chat_response, client

router = APIRouter()

# Password hashing - Support both for backward compatibility
# New passwords will use bcrypt, but can verify existing argon2 hashes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserSignup(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    username: str
    message: str

@router.post("/signup")
async def signup(user: UserSignup):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = pwd_context.hash(user.password)
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    })
    return {"message": "User created successfully"}

@router.post("/login")
async def login(user: UserLogin):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"message": "Login successful", "username": user.username}

@router.post("/chat")
async def chat(chat: ChatMessage):
    # Fetch recent history for context
    recent_history = list(chats_collection.find({"username": chat.username}).sort("timestamp", 1).limit(10))
    
    # Fetch current known event details
    current_event = events_collection.find_one({"username": chat.username}, sort=[("updated_at", -1)])
    if not current_event:
        current_event = {}
        
    # Process message with Groq AI API
    ai_result = generate_chat_response(chat.message, recent_history, current_event)
    bot_response = ai_result.get("response")
    event_date = ai_result.get("event_date")
    location = ai_result.get("location")
    price = ai_result.get("price")
    guests = ai_result.get("guests")
    
    # Save chat history
    chats_collection.insert_one({
        "username": chat.username,
        "user_message": chat.message,
        "bot_response": bot_response,
        "timestamp": datetime.utcnow()
    })
    
    # Save event if data was extracted
    if event_date or price or location or guests:
        # Use upsert with a compound key (username + date + location) to prevent duplicates
        # If the user logs the same date/location again, it will update, not create a duplicate
        query_fields = {"username": chat.username}
        
        # Build update fields - only include non-None values
        update_fields = {"updated_at": datetime.utcnow(), "username": chat.username}
        if event_date is not None: 
            update_fields["date"] = event_date
            query_fields["date"] = event_date
        if location is not None: 
            update_fields["location"] = location
            query_fields["location"] = location
        if price is not None: 
            update_fields["price"] = price
        if guests is not None: 
            update_fields["guests"] = guests
        
        # Use upsert to update existing event or create new one
        # This prevents duplicates when the same date+location is mentioned multiple times
        events_collection.update_one(
            query_fields,
            {"$set": update_fields},
            upsert=True
        )
        
    return {"response": bot_response}

@router.get("/history/{username}")
async def get_history(username: str):
    history = list(chats_collection.find({"username": username}, {"_id": 0}).sort("timestamp", 1))
    return {"history": history}

@router.get("/events/{username}")
async def get_events(username: str):
    # Retrieve all events for the user
    events = list(events_collection.find({"username": username}, {"_id": 0}).sort("updated_at", -1))
    return {"events": events}

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Read the audio file
        audio_content = await file.read()
        
        # We need to pass a tuple (filename, file_content) to the Groq client
        # so it knows the file extension (e.g., .webm or .wav)
        file_tuple = (file.filename, audio_content)
        
        # Call Groq Whisper API
        completion = client.audio.transcriptions.create(
            file=file_tuple,
            model="whisper-large-v3",
            response_format="json"
        )
        
        # The transcription text
        transcription = completion.text
        return {"text": transcription}
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail="Voice transcription failed. Please try again.")
