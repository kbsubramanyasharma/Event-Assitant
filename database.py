from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection string
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)

# Database
db = client.catering_bot_db

# Collections
users_collection = db.users
chats_collection = db.chats
events_collection = db.events

def get_db():
    return db
