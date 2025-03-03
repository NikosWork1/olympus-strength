from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
from datetime import datetime, timedelta
import json

# Database imports
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Olympus Strength")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/img", exist_ok=True)  # For storing images

# Mount static files (CSS, JS, images)
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

# --- Web Routes ---

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    classes = crud.get_classes(db)
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Home", "classes": classes}
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

# --- API Endpoints ---

# Authentication
@app.post("/api/login")
async def login(form_data: schemas.Login, db: Session = Depends(get_db)):
    member = crud.authenticate_member(db, form_data.email, form_data.password)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real app, you'd generate a JWT token here
    return {"email": member.email, "id": member.id, "name": member.name}

# Members
@app.get("/api/members", response_model=List[schemas.Member])
async def get_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    members = crud.get_members(db, skip=skip, limit=limit)
    return members

@app.post("/api/members", response_model=schemas.Member)
async def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    db_member = crud.get_member_by_email(db, member.email)
    if db_member:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_member(db, member)

@app.get("/api/members/{member_id}", response_model=schemas.Member)
async def get_member(member_id: int, db: Session = Depends(get_db)):
    db_member = crud.get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@app.put("/api/members/{member_id}", response_model=schemas.Member)
async def update_member(member_id: int, member: schemas.MemberUpdate, db: Session = Depends(get_db)):
    db_member = crud.update_member(db, member_id=member_id, member=member)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@app.delete("/api/members/{member_id}")
async def delete_member(member_id: int, db: Session = Depends(get_db)):
    success = crud.delete_member(db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"detail": "Member deleted successfully"}

# Workouts
@app.get("/api/workouts", response_model=List[schemas.Workout])
async def get_workouts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workouts = crud.get_workouts(db, skip=skip, limit=limit)
    return workouts

@app.post("/api/workouts", response_model=schemas.Workout)
async def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    return crud.create_workout(db, workout)

@app.get("/api/workouts/{workout_id}", response_model=schemas.Workout)
async def get_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = crud.get_workout(db, workout_id=workout_id)
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@app.put("/api/workouts/{workout_id}", response_model=schemas.Workout)
async def update_workout(workout_id: int, workout: schemas.WorkoutUpdate, db: Session = Depends(get_db)):
    db_workout = crud.update_workout(db, workout_id=workout_id, workout=workout)
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@app.delete("/api/workouts/{workout_id}")
async def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    success = crud.delete_workout(db, workout_id=workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"detail": "Workout deleted successfully"}

# Classes
@app.get("/api/classes", response_model=List[schemas.GymClass])
async def get_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    classes = crud.get_classes(db, skip=skip, limit=limit)
    return classes

@app.post("/api/classes", response_model=schemas.GymClass)
async def create_class(gym_class: schemas.GymClassCreate, db: Session = Depends(get_db)):
    return crud.create_class(db, gym_class)

@app.get("/api/classes/{class_id}", response_model=schemas.GymClass)
async def get_class(class_id: int, db: Session = Depends(get_db)):
    db_class = crud.get_class(db, class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@app.put("/api/classes/{class_id}", response_model=schemas.GymClass)
async def update_class(class_id: int, gym_class: schemas.GymClassUpdate, db: Session = Depends(get_db)):
    db_class = crud.update_class(db, class_id=class_id, gym_class=gym_class)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@app.delete("/api/classes/{class_id}")
async def delete_class(class_id: int, db: Session = Depends(get_db)):
    success = crud.delete_class(db, class_id=class_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"detail": "Class deleted successfully"}

# Bookings
@app.post("/api/bookings", response_model=schemas.Booking)
async def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    # Check if class exists
    db_class = crud.get_class(db, class_id=booking.class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if member exists
    db_member = crud.get_member(db, member_id=booking.member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check capacity by counting existing bookings
    existing_bookings = crud.get_class_bookings(db, class_id=booking.class_id)
    if len(existing_bookings) >= db_class.max_capacity:
        raise HTTPException(status_code=400, detail="Class is at maximum capacity")
    
    return crud.create_booking(db, booking)

@app.get("/api/bookings/member/{member_id}", response_model=List[schemas.Booking])
async def get_member_bookings(member_id: int, db: Session = Depends(get_db)):
    bookings = crud.get_member_bookings(db, member_id=member_id)
    return bookings

@app.get("/api/bookings/class/{class_id}", response_model=List[schemas.Booking])
async def get_class_bookings(class_id: int, db: Session = Depends(get_db)):
    bookings = crud.get_class_bookings(db, class_id=class_id)
    return bookings

@app.put("/api/bookings/{booking_id}", response_model=schemas.Booking)
async def update_booking(booking_id: int, booking: schemas.BookingUpdate, db: Session = Depends(get_db)):
    db_booking = crud.update_booking(db, booking_id=booking_id, booking=booking)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

@app.delete("/api/bookings/{booking_id}")
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    success = crud.delete_booking(db, booking_id=booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"detail": "Booking deleted successfully"}

# Member Workouts
@app.post("/api/member-workouts", response_model=schemas.MemberWorkout)
async def create_member_workout(member_workout: schemas.MemberWorkoutCreate, db: Session = Depends(get_db)):
    # Check if workout exists
    db_workout = crud.get_workout(db, workout_id=member_workout.workout_id)
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Check if member exists
    db_member = crud.get_member(db, member_id=member_workout.member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return crud.create_member_workout(db, member_workout)

@app.get("/api/member-workouts/member/{member_id}", response_model=List[schemas.MemberWorkout])
async def get_member_workouts_list(member_id: int, db: Session = Depends(get_db)):
    workouts = crud.get_member_workouts(db, member_id=member_id)
    return workouts

@app.put("/api/member-workouts/{member_workout_id}", response_model=schemas.MemberWorkout)
async def update_member_workout(member_workout_id: int, member_workout: schemas.MemberWorkoutUpdate, db: Session = Depends(get_db)):
    db_member_workout = crud.update_member_workout(db, member_workout_id=member_workout_id, member_workout=member_workout)
    if db_member_workout is None:
        raise HTTPException(status_code=404, detail="Member workout not found")
    return db_member_workout

@app.delete("/api/member-workouts/{member_workout_id}")
async def delete_member_workout(member_workout_id: int, db: Session = Depends(get_db)):
    success = crud.delete_member_workout(db, member_workout_id=member_workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member workout not found")
    return {"detail": "Member workout deleted successfully"}

# Seed initial data if database is empty
def seed_initial_data():
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

# Run the application
if __name__ == "__main__":
    print("Starting Olympus Strength website...")
    
    # Create tables and seed initial data
    models.Base.metadata.create_all(bind=engine)
    seed_initial_data()
    
    print("Database initialized with seed data.")
    print("Make sure to add some images to the static/img folder for the best experience:")
    print("- Add gym-hero.jpg for the hero background")
    print("- Add gym-cta.jpg for the call-to-action section background")
    
    # Get port from environment variable for Railway deployment
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)