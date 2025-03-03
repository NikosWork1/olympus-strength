from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

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

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="Olympus Strength",
    docs_url=None,  # Disable SwaggerUI in production
    redoc_url=None,  # Disable ReDoc in production
    openapi_url=None  # Disable OpenAPI JSON endpoint in production
)

# Custom HTTPS Redirect Middleware
@app.middleware("http")
async def https_redirect(request: Request, call_next):
    # Check if the request is using HTTP
    if request.url.scheme == "http":
        # Construct HTTPS URL
        https_url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(https_url))
    
    # Add security headers
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "*.up.railway.app", 
        "localhost", 
        "127.0.0.1"
    ]
)

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

# Mount static files
logger.info(f"Static files directory: {os.path.abspath('static')}")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Helper Functions ---
def get_current_member(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        email = token  # Simplified for demonstration
        member = crud.get_member_by_email(db, email)
        if member is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return member
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Seed initial data function
def seed_initial_data() -> Any:
    try:
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
                )
            ]
            
            for workout in workouts:
                crud.create_workout(db, workout)
        
        logger.info("Initial data seeding completed successfully")
    except Exception as e:
        logger.error(f"Error seeding initial data: {e}")
    finally:
        db.close()

# --- Web Routes ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        classes = crud.get_classes(db)
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "title": "Home", 
                "classes": classes
            }
        )
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Members page
@app.get("/members", response_class=HTMLResponse)
async def get_members_page(request: Request, db: Session = Depends(get_db)):
    try:
        members = crud.get_members(db)
        return templates.TemplateResponse(
            "members.html", 
            {"request": request, "title": "Members", "members": members}
        )
    except Exception as e:
        logger.error(f"Error rendering members page: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Workouts page
@app.get("/workouts", response_class=HTMLResponse)
async def get_workouts_page(request: Request, db: Session = Depends(get_db)):
    try:
        workouts = crud.get_workouts(db)
        return templates.TemplateResponse(
            "workouts.html", 
            {"request": request, "title": "Workouts", "workouts": workouts}
        )
    except Exception as e:
        logger.error(f"Error rendering workouts page: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Run the application
if __name__ == "__main__":
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Seed initial data
    seed_initial_data()
    
    # Logging startup information
    logger.info("Olympus Strength application initializing...")
    
    # Get port from environment variable for Railway deployment
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,  # Disable reload in production
        log_level="info"
    )