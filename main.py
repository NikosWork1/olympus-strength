from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Olympus Strength")

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Home page
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

# Initial data seeding function
def seed_initial_data():
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

# Seed initial data
seed_initial_data()

# Optional: For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)