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

@app.get("/classes", response_class=HTMLResponse)
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
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "current_user": current_user,
            "members": members,
            "workouts": workouts,
            "classes": classes
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
        
        return templates.TemplateResponse("coach_dashboard.html", {
            "request": request,
            "current_user": current_user
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
    
    # Create member (always with customer role)
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
async def create_booking_api(request: Request, 
                            booking_data: dict, 
                            db: Session = Depends(get_db)):
    try:
        logger.info(f"Received booking data: {booking_data}")
        
        # Get current user
        current_user = await get_optional_user(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Create booking object
        booking = schemas.BookingCreate(
            class_id=booking_data["class_id"],
            member_id=current_user.id,
            class_date=booking_data["class_date"]
        )
        
        # Create the booking
        db_booking = crud.create_booking(db=db, booking=booking)
        
        return db_booking
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error booking class: {str(e)}")

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

# Route to view current user's bookings
# This endpoint displays all bookings for the currently logged-in user
# Authentication is required to access this endpoint
@app.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings(request: Request, db: Session = Depends(get_db)):
    # Get the current authenticated user
    current_user = await get_optional_user(request, db)
    
    # Check if user is authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Retrieve only the current user's bookings from the database
    bookings = db.query(models.Booking).filter(models.Booking.member_id == current_user.id).all()
    
    # Prepare data with additional details for template rendering
    booking_details = []
    for booking in bookings:
        # Get class details for this booking
        gym_class = db.query(models.GymClass).filter(models.GymClass.id == booking.class_id).first()
        
        # Add enriched booking information to our list
        booking_details.append({
            "id": booking.id,
            "class_name": gym_class.name if gym_class else "Unknown",
            "class_instructor": gym_class.instructor if gym_class else "Unknown",
            "booking_date": booking.booking_date,
            "class_date": booking.class_date,
            "status": booking.status
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

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
