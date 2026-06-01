# 🍽️ Catering AI Chatbot

A smart, AI-driven assistant designed specifically for catering staff and event workers. This chatbot allows workers to effortlessly log their upcoming shifts through natural conversation (text or voice), automatically extracts key details, and organizes them into a personal dashboard. It also sends automated email reminders for upcoming jobs.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-47A248.svg)

## ✨ Key Features

- **🗣️ Natural Language Chat:** Converse naturally with the AI to log shifts. It understands context and remembers conversation history.
- **🧩 Smart Data Extraction:** Automatically identifies and extracts:
  - **Date** (e.g., "next Friday", "March 18th")
  - **Location** (e.g., "Bangalore Palace", "Grand Hotel")
  - **Guest Count** (e.g., "100 pax", "500 people")
  - **Salary/Pay** (e.g., "₹2500", "5000 rupees")
- **🎙️ Voice Support:** Built-in voice recorder with accurate transcription (powered by Groq Whisper) for hands-free logging.
- **📅 Shift Dashboard:** "My Bookings" view organizes all your logged shifts in a clean, tabular format.
- **⏰ Automated Reminders:** Background scheduler checks daily at 9:00 AM and emails you reminders for shifts scheduled the next day.
- **🔒 Secure Authentication:** Email/Password login system secured with industry-standard Argon2/Bcrypt hashing.
- **🔄 Smart Updates:** Intelligently updates existing bookings if you mention new details for the same date and location, preventing duplicate entries.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI
- **Database:** MongoDB
- **AI & NLP:** Groq API (High-performance LLM inference), Groq Whisper (Speech-to-Text)
- **Frontend:** HTML5, CSS3 (Glassmorphism design), Vanilla JavaScript
- **Task Scheduling:** APScheduler (Advanced Python Scheduler)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB installed and running locally (or a MongoDB Atlas URI)
- A [Groq API Key](https://console.groq.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kbsubramanyasharma/Event-Assitant.git
   cd catering-chatbot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database
   MONGO_URL=mongodb://localhost:27017/
   
   # AI Provider
   GROQ_API_KEY=your_groq_api_key_here
   
   # Email Service (Optional, for reminders)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ```

### Running the Application

1. **Start the server:**
   ```bash
   python main.py
   ```
   The backend server will start on `http://127.0.0.1:8000`.

2. **Access the App:**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

## 📖 Usage Guide

1. **Sign Up/Login:** Create an account using your email address.
2. **Log a Shift:** 
   - Type: *"I have a wedding catering gig at the Grand Hotel on March 25th for 300 guests, pay is 2000."*
   - Voice: Click the microphone icon 🎙️ and speak naturally.
3. **View Bookings:** Click "My Bookings" in the sidebar to visualize your schedule.
4. **Update Details:** Just mention the change in chat. *"Actually, the pay for the Grand Hotel event is 2500."*

## 📁 Project Structure

```
catering_chatbot/
├── main.py              # Application entry point & configuration
├── routes.py            # API endpoints (Auth, Chat, Logging)
├── chatbot.py           # AI logic & Groq client interaction
├── database.py          # MongoDB connection & collections
├── email_service.py     # Background scheduler & email logic
├── requirements.txt     # Python dependencies
└── frontend/            # Static frontend files
    ├── index.html       # Login/Signup page
    ├── chat.html        # Main dashboard interface
    ├── app.js           # Frontend logic & API calls
    └── style.css        # Styling
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
