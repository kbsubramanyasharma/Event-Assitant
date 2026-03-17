from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from routes import router

from email_service import scheduler

app = FastAPI(title="AI Catering Chatbot")

@app.on_event("startup")
def startup_event():
    print("Starting background APScheduler...")
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down APScheduler...")
    scheduler.shutdown()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Create frontend directory if it doesn't exist
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)

# Mount static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def read_root():
    return RedirectResponse(url="/frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
