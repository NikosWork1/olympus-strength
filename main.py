from fastapi import FastAPI, Request, Depends, HTTPException, Response, Form, Cookie, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db
import os
import logging
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List, Union
from passlib.context import CryptContext
import secrets
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Olympus Strength")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Create route handlers
@app.get("/workouts/personal", response_class=HTMLResponse)
async def my_workouts(request: Request, db: Session = Depends(get_db)):
    current_user = await get_optional_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Get the user's workouts
    user_workouts = crud.get_member_workouts(db, current_user.id)
    
    return templates.TemplateResponse("my_workouts.html", {
        "request": request,
        "current_user": current_user,
        "workouts": user_workouts
    })

@app.get("/book_class", response_class=HTMLResponse)
async def book_class(request: Request, db: Session = Depends(get_db)):
    current_user = await get_optional_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Get available classes
    classes = crud.get_classes(db)
    
    return templates.TemplateResponse("book_class.html", {
        "request": request,
        "current_user": current_user,
        "classes": classes
    })

# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Get password hash
def get_password_hash(password):
    return pwd_context.hash(password)

# Try to get current user (returns None if not authenticated)
async def get_optional_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = crud.get_member_by_email(db, email=username)
        return user
    except JWTError:
        return None

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_optional_user(request, db)
        print(f"User role: {current_user.role if current_user else 'None'}")  # Debug print
        return templates.TemplateResponse("index.html", {
            "request": request,
            "current_user": current_user
        })
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Members page
@app.get("/members", response_class=HTMLResponse)
async def get_members_page(request: Request, db: Session = Depends(get_db)):
    try:
        members = crud.get_members(db)
        current_user = await get_optional_user(request, db)
        return templates.TemplateResponse("members.html", {
            "request": request,
            "members": members,
            "current_user": current_user
        })
    except Exception as e:
        logger.error(f"Error rendering members page: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Admin dashboard
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        # Get current user and verify they are an admin
        current_user = await get_optional_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=303)
        
        if current_user.role != "admin":
            return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Denied</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Access Denied</h1>
    <p>You do not have permission to access this page. This area is restricted to administrators only.</p>
    <p><a href="/">Return to Home</a></p>
</body>
</html>
            """, status_code=403)
        
        # Get data for the dashboard
        members = crud.get_members(db)
        workouts = crud.get_workouts(db)
        classes = crud.get_classes(db)
        financial_summary = crud.get_financial_summary(db)
        recent_transactions = crud.get_recent_transactions(db, limit=10)
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "current_user": current_user,
            "members": members,
            "workouts": workouts,
            "classes": classes,
            "financial_summary": financial_summary,
            "recent_transactions": recent_transactions
        })
    except Exception as e:
        logger.error(f"Error rendering admin dashboard: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Coach dashboard
@app.get("/coach/dashboard", response_class=HTMLResponse)
async def coach_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        # Get current user and verify they are a coach
        current_user = await get_optional_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=303)
        
        if current_user.role != "coach":
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Access Denied</title>
                <style>
                    body {{
                        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .error {{
                        color: #F44336;
                    }}
                </style>
            </head>
            <body>
                <h1 class="error">Access Denied</h1>
                <p>You do not have permission to access this page. This area is restricted to coaches only.</p>
                <p><a href="/">Return to Home</a></p>
            </body>
            </html>
            """, status_code=403)
        
        # Get real data for the dashboard
        # 1. Get coach's clients
        clients = db.query(models.Member).filter(
            models.Member.role == "customer"
        ).limit(10).all()
        
        # 2. Get total client count
        client_count = db.query(models.Member).filter(
            models.Member.role == "customer"
        ).count()
        
        # 3. Get workout count for this coach
        workout_count = db.query(models.CoachWorkout).filter(
            models.CoachWorkout.coach_id == current_user.id
        ).count()
        
        # 4. Get today's session count (bookings)
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        session_count = db.query(models.Booking).filter(
            models.Booking.class_date >= today_start,
            models.Booking.class_date <= today_end
        ).count()
        
        # 5. Get today's schedule (bookings)
        today_schedule = db.query(models.Booking, models.GymClass, models.Member).join(
            models.GymClass, models.Booking.class_id == models.GymClass.id
        ).join(
            models.Member, models.Booking.member_id == models.Member.id
        ).filter(
            models.Booking.class_date >= today_start,
            models.Booking.class_date <= today_end
        ).all()
        
        # 6. Get coach's workouts
        workouts = db.query(models.Workout).join(
            models.CoachWorkout, models.Workout.id == models.CoachWorkout.workout_id
        ).filter(
            models.CoachWorkout.coach_id == current_user.id
        ).all()
        
        return templates.TemplateResponse("coach_dashboard.html", {
            "request": request,
            "current_user": current_user,
            "clients": clients,
            "client_count": client_count,
            "workout_count": workout_count,
            "session_count": session_count,
            "today_schedule": today_schedule,
            "workouts": workouts
            })
    except Exception as e:
        logger.error(f"Error rendering coach dashboard: {e}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error</title>
            <style>
                body {{
                    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .error {{
                    color: #F44336;
                }}
            </style>
        </head>
        <body>
            <h1 class="error">Internal Server Error</h1>
            <p>We're sorry, something went wrong on our end. Please try again later.</p>
            <p>Error details: {str(e)}</p>
        </body>
        </html>
        """)


# Workouts page
@app.get("/workouts", response_class=HTMLResponse)
async def get_workouts_page(request: Request, db: Session = Depends(get_db)):
    try:
        workouts = crud.get_workouts(db)
        current_user = await get_optional_user(request, db)
        return templates.TemplateResponse("workouts.html", {
            "request": request,
            "workouts": workouts,
            "current_user": current_user
        })
    except Exception as e:
        logger.error(f"Error rendering workouts page: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Profile page
@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_optional_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=303)
        
        # Get user workouts, stats, etc.
        member_workouts = crud.get_member_workouts(db, current_user.id)
        
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "current_user": current_user,
            "workouts": member_workouts
        })
    except Exception as e:
        logger.error(f"Error rendering profile page: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login post
@app.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    member = crud.get_member_by_email(db, form_data.username)
    if not member or not verify_password(form_data.password, member.password_hash):
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": {"method": "GET"},
                "error": "Invalid email or password"
            },
            status_code=401
        )
    
    # Create access token - MAKE SURE TO INCLUDE THE ROLE
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member.email, "role": member.role}, expires_delta=access_token_expires
    )
    
    # Set cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return response

# Signup page
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Updated signup route
@app.post("/signup")
async def signup(
    response: Response,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    membership_type: str = Form(...),
    role: str = Form("customer"),  # Default to customer role
    db: Session = Depends(get_db)
):
    # Force role to be customer for public signups
    role = "customer"
    
    # Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html", 
            {
                "request": {"method": "GET"},
                "error": "Passwords do not match",
                "form_data": {
                    "name": name,
                    "email": email,
                    "membership_type": membership_type
                }
            },
            status_code=400
        )
    
    # Check if user already exists
    existing_user = crud.get_member_by_email(db, email)
    if existing_user:
        return templates.TemplateResponse(
            "signup.html", 
            {
                "request": {"method": "GET"},
                "error": "Email already registered",
                "form_data": {
                    "name": name,
                    "membership_type": membership_type
                }
            },
            status_code=400
        )
    
    # Create member
    member = crud.create_member(db, schemas.MemberCreate(
        name=name,
        email=email,
        password=password,
        phone="",
        membership_type=membership_type,
        role=role
    ))
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member.email, "role": member.role}, expires_delta=access_token_expires
    )
    
    # Set cookie and redirect
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return response

# Logout
@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

# API routes for CRUD operations
@app.post("/api/members", response_model=schemas.Member)
def create_member_api(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    db_member = crud.get_member_by_email(db, email=member.email)
    if db_member:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_member(db=db, member=member)

@app.get("/api/members", response_model=List[schemas.Member])
def read_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    members = crud.get_members(db, skip=skip, limit=limit)
    return members

@app.get("/api/members/{member_id}", response_model=schemas.Member)
def read_member(member_id: int, db: Session = Depends(get_db)):
    db_member = crud.get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@app.put("/api/members/{member_id}", response_model=schemas.Member)
def update_member_api(member_id: int, member: schemas.MemberUpdate, db: Session = Depends(get_db)):
    db_member = crud.update_member(db, member_id=member_id, member=member)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@app.delete("/api/members/{member_id}")
def delete_member_api(member_id: int, db: Session = Depends(get_db)):
    success = crud.delete_member(db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"success": True}

@app.post("/api/workouts", response_model=schemas.Workout)
def create_workout_api(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    return crud.create_workout(db=db, workout=workout)

@app.get("/api/workouts", response_model=List[schemas.Workout])
def read_workouts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workouts = crud.get_workouts(db, skip=skip, limit=limit)
    return workouts

# 404 page
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - Olympus Strength</title>
    <style>
        body {
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            flex-direction: column;
            text-align: center;
            padding: 0 1rem;
        }
        
        .error-container {
            max-width: 600px;
        }
        
        h1 {
            font-size: 5rem;
            margin: 0;
            color: #4CAF50;
        }
        
        h2 {
            font-size: 2rem;
            margin-top: 0;
            margin-bottom: 1.5rem;
        }
        
        p {
            font-size: 1.1rem;
            margin-bottom: 2rem;
            color: #757575;
        }
        
        .btn {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            box-shadow: 0 4px 6px rgba(76, 175, 80, 0.2);
        }
        
        .btn:hover {
            background-color: #388E3C;
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you're looking for doesn't exist or has been moved. Return to our homepage to continue your fitness journey.</p>
        <a href="/" class="btn">Go Home</a>
    </div>
</body>
</html>""",
        status_code=404
    )

# API endpoint for creating new class bookings
# This endpoint handles POST requests to create a new booking
# It validates request data, authenticates the user, and saves the booking to the database
# Returns the created booking object or an error message
@app.post("/api/bookings", response_model=schemas.Booking)
async def create_booking_api(
    request: Request, 
    booking_data: dict,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received booking data: {booking_data}")
        
        # Get current user
        current_user = await get_optional_user(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        logger.info(f"Current user: {current_user.name} (ID: {current_user.id})")
        
        # Verify the required fields are present
        if 'class_id' not in booking_data:
            raise HTTPException(status_code=400, detail="Missing class_id field")
        if 'class_date' not in booking_data:
            raise HTTPException(status_code=400, detail="Missing class_date field")
            
        # Parse the class_date into a datetime object
        try:
            class_date = datetime.fromisoformat(booking_data["class_date"])
            logger.info(f"Parsed class_date: {class_date}")
        except ValueError as e:
            logger.error(f"Error parsing date: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
            
        # Create booking object
        booking = schemas.BookingCreate(
            class_id=booking_data["class_id"],
            member_id=current_user.id,
            class_date=class_date
        )
        
        # Check if the class exists
        gym_class = db.query(models.GymClass).filter(models.GymClass.id == booking.class_id).first()
        if not gym_class:
            raise HTTPException(status_code=404, detail=f"Class with ID {booking.class_id} not found")
        
        # Check if there's already a booking for this user, class, and date
        existing_booking = db.query(models.Booking).filter(
            models.Booking.member_id == booking.member_id,
            models.Booking.class_id == booking.class_id,
            models.Booking.class_date == booking.class_date
        ).first()
        
        if existing_booking:
            raise HTTPException(status_code=400, detail="You've already booked this class for this date and time")
            
        # Check if class is full (compare against max_capacity)
        bookings_count = db.query(models.Booking).filter(
            models.Booking.class_id == booking.class_id,
            models.Booking.class_date == booking.class_date,
            models.Booking.status != "cancelled"
        ).count()
        
        if bookings_count >= gym_class.max_capacity:
            raise HTTPException(status_code=400, detail="This class is full for the selected date and time")
        
        # Create the booking
        db_booking = crud.create_booking(db=db, booking=booking)
        logger.info(f"Booking created: {db_booking.id}")
        
        return db_booking
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating booking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Route to view all bookings (admin & coach access only)
# This endpoint displays all bookings in the system with member and class details
# Access is restricted to users with admin or coach roles
@app.get("/admin/bookings", response_class=HTMLResponse)
async def view_bookings(request: Request, db: Session = Depends(get_db)):
    # Get the current authenticated user
    current_user = await get_optional_user(request, db)
    
    # Check if user is authenticated and has proper permissions
    if not current_user or current_user.role not in ["admin", "coach"]:
        return RedirectResponse(url="/login", status_code=303)
    
    # Retrieve all bookings from the database
    bookings = db.query(models.Booking).all()
    
    # Prepare data with additional details for template rendering
    booking_details = []
    for booking in bookings:
        # Get member details for this booking
        member = db.query(models.Member).filter(models.Member.id == booking.member_id).first()
        
        # Get class details for this booking
        gym_class = db.query(models.GymClass).filter(models.GymClass.id == booking.class_id).first()
        
        # Add enriched booking information to our list
        booking_details.append({
            "id": booking.id,
            "member_name": member.name if member else "Unknown",
            "class_name": gym_class.name if gym_class else "Unknown",
            "booking_date": booking.booking_date,
            "class_date": booking.class_date,
            "status": booking.status
        })
    
    # Render the template with all booking details
    return templates.TemplateResponse("admin_bookings.html", {
        "request": request,
        "current_user": current_user,
        "bookings": booking_details
    })

@app.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings(request: Request, db: Session = Depends(get_db)):
    # Get the current authenticated user
    current_user = await get_optional_user(request, db)
    
    # Check if user is authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Use the enhanced get_member_bookings function that includes class details
    bookings = crud.get_member_bookings(db, current_user.id)
    
    # Render the template with the enhanced bookings
    return templates.TemplateResponse("my_bookings.html", {
        "request": request,
        "current_user": current_user,
        "bookings": bookings
    })
    
    # Render the template with the user's booking details
    return templates.TemplateResponse("my_bookings.html", {
        "request": request,
        "current_user": current_user,
        "bookings": booking_details
    })


# Maps page
@app.get("/maps", response_class=HTMLResponse)
async def maps_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_optional_user(request, db)
        return templates.TemplateResponse("maps.html", {
            "request": request,
            "current_user": current_user,
            "title": "Find Us"
        })
    except Exception as e:
        logger.error(f"Error rendering maps page: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Contact page
@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_optional_user(request, db)
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "current_user": current_user,
            "title": "Contact Us"
        })
    except Exception as e:
        logger.error(f"Error rendering contact page: {e}")
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            color: #F44336;
        }}
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Contact form submission handler
@app.post("/contact", response_class=HTMLResponse)
async def contact_form_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_optional_user(request, db)
        
        # In a real application, you would send an email or store the message
        # For now, we'll just show a success message
        
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "current_user": current_user,
            "title": "Contact Us",
            "success_message": "Thank you for your message! We will get back to you soon."
        })
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "current_user": current_user,
            "title": "Contact Us",
            "error_message": "There was an error processing your message. Please try again."
        })

# Temporary route to create staff accounts
@app.get("/create-staff-accounts")
async def create_staff_accounts_route(db: Session = Depends(get_db)):
    # Staff account data
    coaches = [
        {
            "name": "Alex Hermes",
            "email": "alex@olympusstrength.com",
            "password": "olympus2025",
            "phone": "+30 210 5555 101",
            "role": "coach"
        },
        {
            "name": "Marcus Leonidas",
            "email": "marcus@olympusstrength.com",
            "password": "olympus2025",
            "phone": "+30 210 5555 102",
            "role": "coach"
        },
        {
            "name": "Helena Troy",
            "email": "helena@olympusstrength.com", 
            "password": "olympus2025",
            "phone": "+30 210 5555 103",
            "role": "coach"
        },
        {
            "name": "Diana Artemis",
            "email": "diana@olympusstrength.com",
            "password": "olympus2025",
            "phone": "+30 210 5555 104", 
            "role": "coach"
        },
        {
            "name": "Jason Argos",
            "email": "jason@olympusstrength.com",
            "password": "olympus2025",
            "phone": "+30 210 5555 105",
            "role": "coach"
        }
    ]

    admin = {
        "name": "Zeus Olympian",
        "email": "admin@olympusstrength.com",
        "password": "admin2025",
        "phone": "+30 210 5555 100",
        "role": "admin"
    }
    
    created_accounts = []

    try:
        # Create coach accounts
        for coach_data in coaches:
            # Check if account already exists
            existing_coach = crud.get_member_by_email(db, coach_data["email"])
            if existing_coach:
                created_accounts.append(f"Coach {coach_data['name']} already exists.")
                continue
                
            # Create coach account
            coach = schemas.MemberCreate(
                name=coach_data["name"],
                email=coach_data["email"],
                password=coach_data["password"],
                phone=coach_data["phone"],
                membership_type="None",
                role=coach_data["role"]
            )
            db_coach = crud.create_member(db, coach)
            created_accounts.append(f"Created coach account: {db_coach.name} ({db_coach.email})")
        
        # Create admin account
        existing_admin = crud.get_member_by_email(db, admin["email"])
        if existing_admin:
            created_accounts.append(f"Admin {admin['name']} already exists.")
        else:
            admin_user = schemas.MemberCreate(
                name=admin["name"],
                email=admin["email"],
                password=admin["password"],
                phone=admin["phone"],
                membership_type="None",
                role=admin["role"]
            )
            db_admin = crud.create_member(db, admin_user)
            created_accounts.append(f"Created admin account: {db_admin.name} ({db_admin.email})")
            
        return {
            "message": "Staff accounts created successfully",
            "details": created_accounts,
            "login_credentials": {
                "coaches": [{"name": coach["name"], "email": coach["email"], "password": coach["password"]} for coach in coaches],
                "admin": {"name": admin["name"], "email": admin["email"], "password": admin["password"]}
            }
        }
    except Exception as e:
        logger.error(f"Error creating staff accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating staff accounts: {str(e)}")

@app.post("/api/workouts/create")
async def create_workout_with_coach(
    request: Request,
    workout_data: dict,
    db: Session = Depends(get_db)
):
    try:
        # Get current user
        current_user = await get_optional_user(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Create workout object
        workout = schemas.WorkoutCreate(
            name=workout_data["name"],
            description=workout_data["description"],
            difficulty=workout_data["difficulty"],
            category=workout_data.get("category", ""),
            duration=workout_data.get("duration", 45),
            calories=workout_data.get("calories", 300)
        )
        
        # Create the workout
        db_workout = crud.create_workout(db=db, workout=workout)
        
        # If user is a coach, assign workout to them
        if current_user.role == "coach":
            crud.assign_workout_to_coach(db, db_workout.id, current_user.id)
        # If user is admin and workout has a coach_id, assign to that coach
        elif current_user.role == "admin" and "coach_id" in workout_data:
            crud.assign_workout_to_coach(db, db_workout.id, workout_data["coach_id"])
        
        return db_workout
    except Exception as e:
        logger.error(f"Error creating workout: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error creating workout: {str(e)}")

# Add this route to main.py for getting coach workouts

@app.get("/api/coaches/{coach_id}/workouts")
async def get_coach_workouts(
    coach_id: int,
    db: Session = Depends(get_db)
):
    # Get the coach
    coach = db.query(models.Member).filter(
        models.Member.id == coach_id,
        models.Member.role == "coach"
    ).first()
    
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    # Get workouts created by this coach
    coach_workouts = db.query(models.CoachWorkout).filter(
        models.CoachWorkout.coach_id == coach_id
    ).all()
    
    # Get the actual workout objects
    workouts = []
    for coach_workout in coach_workouts:
        workout = db.query(models.Workout).filter(
            models.Workout.id == coach_workout.workout_id
        ).first()
        if workout:
            workouts.append(workout)
    
    return workouts

# In main.py, let's fix the my-bookings route:

@app.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings(request: Request, db: Session = Depends(get_db)):
    # Get the current authenticated user
    current_user = await get_optional_user(request, db)

    # Check if user is authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    # Retrieve bookings from the database with error handling
    try:
        # Get all bookings for this user
        bookings = db.query(models.Booking).filter(models.Booking.member_id == current_user.id).all()

        # Safely get class details with error handling
        booking_details = []
        for booking in bookings:
            try:
                # Get class details for this booking with error handling
                gym_class = db.query(models.GymClass).filter(models.GymClass.id == booking.class_id).first()

                booking_details.append({
                    "id": booking.id,
                    "class_name": gym_class.name if gym_class else "Unknown",
                    "class_instructor": gym_class.instructor if gym_class else "Unknown",
                    "booking_date": booking.booking_date,
                    "class_date": booking.class_date,
                    "status": booking.status
                })
            except Exception as e:
                logger.error(f"Error processing booking {booking.id}: {e}")
                # Add a placeholder for the problematic booking
                booking_details.append({
                    "id": booking.id,
                    "class_name": "Error loading class",
                    "class_instructor": "N/A",
                    "booking_date": booking.booking_date,
                    "class_date": booking.class_date,
                    "status": "Error"
                })

        # Render the template with the user's booking details
        return templates.TemplateResponse("my_bookings.html", {
            "request": request,
            "current_user": current_user,
            "bookings": booking_details
        })
    except Exception as e:
        logger.error(f"Error in my_bookings route: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "There was an error loading your bookings. Please try again later.",
            "current_user": current_user
        })

@app.post("/api/workouts/create", response_model=schemas.Workout)
async def create_workout_api(
    request: Request, 
    workout_data: schemas.WorkoutCreate,
    db: Session = Depends(get_db)
):
    try:
        # Get current user
        current_user = await get_optional_user(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Create workout object
        db_workout = crud.create_workout(db=db, workout=workout_data)
        
        # If user is a coach, assign workout to them
        if current_user.role == "coach":
            crud.assign_workout_to_coach(db, db_workout.id, current_user.id)
        
        return db_workout
    except Exception as e:
        logger.error(f"Error creating workout: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error creating workout: {str(e)}")

@app.delete("/api/workouts/{workout_id}")
async def delete_workout_api(
    workout_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Get current user
        current_user = await get_optional_user(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if workout exists and belongs to this coach
        if current_user.role == "coach":
            coach_workout = db.query(models.CoachWorkout).filter(
                models.CoachWorkout.workout_id == workout_id,
                models.CoachWorkout.coach_id == current_user.id
            ).first()
            
            if not coach_workout:
                raise HTTPException(status_code=404, detail="Workout not found or you don't have permission")
        
        # Delete the workout
        success = crud.delete_workout(db, workout_id=workout_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workout not found or could not be deleted")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workout: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting workout: {str(e)}")

#Gallery section
@app.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request, db: Session = Depends(get_db)):
    current_user = await get_optional_user(request, db)
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "current_user": current_user
    })

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
