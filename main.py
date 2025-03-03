from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from typing import List, Optional, Any
import uvicorn
import os
from datetime import datetime, timedelta
import json
import logging

# Database imports
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Olympus Strength")

# Add HTTPS redirect middleware
app.add_middleware(HTTPSRedirectMiddleware)

# Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Be careful in production
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "upgrade-insecure-requests; default-src https:; script-src https: 'self'; style-src https: 'self';"
    return response

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/img", exist_ok=True)  # For storing images

# Mount static files (CSS, JS, images)
logger.info(f"Static files directory: {os.path.abspath('static')}")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Helper Functions ---
def get_current_member(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # This is simplified - in a production app, you'd use JWT tokens
    try:
        email = token  # In a real app, decode the JWT token
        member = crud.get_member_by_email(db, email)
        if member is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return member
    except:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Seed initial data function
def seed_initial_data() -> Any:
    db = next(get_db())
    
    # Check if we already have data
    if db.query(models.GymClass).count() == 0:
        # Create classes
        classes = [
            schemas.GymClassCreate(
                name="Olympic Weightlifting",
                description="Master the snatch and clean & jerk with expert technique coaching for maximum power development.",
                instructor="Alex Hermes",
                schedule="Mon, Wed, Fri - 7:00 AM",
                level="All Levels",
                max_capacity=15
            ),
            schemas.GymClassCreate(
                name="Spartan HIIT",
                description="High-intensity interval training inspired by warrior conditioning to push your limits and maximize calorie burn.",
                instructor="Marcus Leonidas",
                schedule="Tue, Thu - 6:00 PM",
                level="Intermediate",
                max_capacity=20
            ),
            schemas.GymClassCreate(
                name="Strength Foundations",
                description="Master fundamental lifts with expert coaching to build the foundation for legendary strength.",
                instructor="Helena Troy",
                schedule="Mon, Wed - 5:30 PM",
                level="Beginner",
                max_capacity=12
            )
        ]
        
        for gym_class in classes:
            crud.create_class(db, gym_class)
    
    # Seed workouts if empty
    if db.query(models.Workout).count() == 0:
        # Create workouts
        workouts = [
            schemas.WorkoutCreate(
                name="Spartan Challenge",
                description="Complete this intense circuit workout inspired by ancient Spartan training.",
                difficulty="Advanced",
                category="Circuit"
            ),
            schemas.WorkoutCreate(
                name="Olympian Circuit",
                description="High intensity cardio and strength training fit for the gods.",
                difficulty="Intermediate",
                category="Cardio"
            ),
            schemas.WorkoutCreate(
                name="Hercules Strength",
                description="Build legendary strength with this compound movement focused routine.",
                difficulty="Intermediate",
                category="Strength"
            )
        ]
        
        for workout in workouts:
            crud.create_workout(db, workout)
    
    # Close the database session
    db.close()

# --- Web Routes ---

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # Ensure base URL is HTTPS
    base_url = f"https://{request.headers.get('host', 'olympus-strength-production.up.railway.app')}"
    
    classes = crud.get_classes(db)
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "title": "Home", 
            "classes": classes,
            "base_url": base_url
        }
    )

# Members page
@app.get("/members", response_class=HTMLResponse)
async def get_members_page(request: Request, db: Session = Depends(get_db)):
    members = crud.get_members(db)
    return templates.TemplateResponse(
        "members.html", 
        {"request": request, "title": "Members", "members": members}
    )

# Workouts page
@app.get("/workouts", response_class=HTMLResponse)
async def get_workouts_page(request: Request, db: Session = Depends(get_db)):
    workouts = crud.get_workouts(db)
    return templates.TemplateResponse(
        "workouts.html", 
        {"request": request, "title": "Workouts", "workouts": workouts}
    )

# (Rest of the routes remain the same as in your original main.py)
# ... (all API endpoints from your original file)

# Run the application
if __name__ == "__main__":
    print("Starting Olympus Strength website...")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Seed initial data
    seed_initial_data()
    
    print("Database initialized with seed data.")
    print("Make sure to add some images to the static/img folder for the best experience:")
    print("- Add gym-hero.jpg for the hero background")
    print("- Add gym-cta.jpg for the call-to-action section background")
    
    # Get port from environment variable for Railway deployment
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)