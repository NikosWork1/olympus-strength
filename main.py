from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db
from typing import List
import os
import logging
from datetime import timedelta, datetime
import jwt
from jwt.exceptions import PyJWTError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Olympus Strength")

# Secret key for JWT token
SECRET_KEY = os.getenv("SECRET_KEY", "olympusstrength2025secretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

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

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token generation function
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = crud.get_member_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# --- API Endpoints ---

# Login API endpoint
@app.post("/api/login")
async def login(form_data: schemas.Login, db: Session = Depends(get_db)):
    user = crud.authenticate_member(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer"
    }

# Create member API endpoint
@app.post("/api/members", response_model=schemas.Member)
def create_member_api(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    db_member = crud.get_member_by_email(db, email=member.email)
    if db_member:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_member(db=db, member=member)

# Delete member API endpoint
@app.delete("/api/members/{member_id}")
def delete_member_api(member_id: int, db: Session = Depends(get_db)):
    if crud.delete_member(db, member_id):
        return {"detail": "Member deleted successfully"}
    raise HTTPException(status_code=404, detail="Member not found")

# Get all members API endpoint
@app.get("/api/members", response_model=List[schemas.Member])
def read_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    members = crud.get_members(db, skip=skip, limit=limit)
    return members

# Get member by ID API endpoint
@app.get("/api/members/{member_id}", response_model=schemas.Member)
def read_member(member_id: int, db: Session = Depends(get_db)):
    db_member = crud.get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

# --- Page Routes ---

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

# User management page (protected, requires login)
@app.get("/admin/users", response_class=HTMLResponse)
async def get_user_management_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(get_current_user)
):
    try:
        # Only allow access if user has a special role (could check if admin)
        members = crud.get_members(db)
        return templates.TemplateResponse(
            "user_management.html", 
            {"request": request, "title": "User Management", "members": members}
        )
    except Exception as e:
        logger.error(f"Error rendering user management page: {e}")
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
                
        # Seed a test user if no users exist
        if db.query(models.Member).count() == 0:
            test_user = schemas.MemberCreate(
                name="Test User",
                email="test@olympusstrength.com",
                password="testpassword123",
                phone="555-123-4567",
                membership_type="Premium"
            )
            crud.create_member(db, test_user)
        
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