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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Olympus Strength")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

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
        user = crud.get_user_by_email(db, email=username)
        return user
    except JWTError:
        return None

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        classes = crud.get_classes(db)
        current_user = await get_optional_user(request, db)
        
        # Generate classes HTML
        classes_html = ""
        for cls in classes:
            classes_html += f"""
            <div class="program-card">
                <div class="program-header">
                    <h3>{cls.name}</h3>
                    <span class="program-badge">{cls.level}</span>
                </div>
                <div class="program-content">
                    <p>{cls.description}</p>
                    <div class="program-details">
                        <span>🧑‍🏫 {cls.trainer}</span>
                        <span>📅 {cls.schedule}</span>
                    </div>
                    <a href="/classes/{cls.id}" class="btn">Book Class</a>
                </div>
            </div>
            """
        
        # If no classes found
        if not classes_html:
            classes_html = """
            <div class="program-card">
                <div class="program-header">
                    <h3>Olympic Weightlifting</h3>
                    <span class="program-badge">All Levels</span>
                </div>
                <div class="program-content">
                    <p>Master the snatch and clean & jerk with expert technique coaching for maximum power development.</p>
                    <div class="program-details">
                        <span>🧑‍🏫 Alex Hermes</span>
                        <span>📅 Mon, Wed, Fri</span>
                    </div>
                    <a href="#" class="btn">Book Class</a>
                </div>
            </div>
            
            <div class="program-card">
                <div class="program-header">
                    <h3>Spartan HIIT</h3>
                    <span class="program-badge">Intermediate</span>
                </div>
                <div class="program-content">
                    <p>High-intensity interval training inspired by warrior conditioning to push your limits and maximize calorie burn.</p>
                    <div class="program-details">
                        <span>🧑‍🏫 Marcus Leonidas</span>
                        <span>📅 Tue, Thu</span>
                    </div>
                    <a href="#" class="btn">Book Class</a>
                </div>
            </div>
            
            <div class="program-card">
                <div class="program-header">
                    <h3>Strength Foundations</h3>
                    <span class="program-badge">Beginner</span>
                </div>
                <div class="program-content">
                    <p>Master fundamental lifts with expert coaching to build the foundation for legendary strength.</p>
                    <div class="program-details">
                        <span>🧑‍🏫 Helena Troy</span>
                        <span>📅 Mon, Wed</span>
                    </div>
                    <a href="#" class="btn">Book Class</a>
                </div>
            </div>
            """
        
        # Render login/signup buttons based on authentication status
        auth_buttons = '<a href="/login" class="nav-link">Login</a><a href="/signup" class="btn">Join Now</a>'
        if current_user:
            auth_buttons = f'<a href="/profile" class="nav-link">Profile</a><a href="/logout" class="nav-link">Logout</a>'
        
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Olympus Strength - Forge Your Legacy</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <header>
        <div class="container header-container">
            <a href="/" class="logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </a>
            
            <button class="mobile-toggle">☰</button>
            
            <nav class="nav">
                <a href="/" class="nav-link">Home</a>
                <a href="/members" class="nav-link">Members</a>
                <a href="/workouts" class="nav-link">Workouts</a>
                {auth_buttons}
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="hero-content">
            <h1>FORGE YOUR LEGACY AT OLYMPUS STRENGTH</h1>
            <p>Where gods train. Where legends are made. Your journey to greatness begins here.</p>
            <a href="#programs" class="btn btn-cta btn-lg">START YOUR JOURNEY</a>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2 class="section-title">WHY CHOOSE OLYMPUS STRENGTH</h2>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">💪</div>
                    <h3>State-of-the-Art Equipment</h3>
                    <p>Train with the latest fitness technology and premium equipment for maximum results.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">👨‍🏫</div>
                    <h3>Expert Trainers</h3>
                    <p>Our certified professionals create personalized programs to help you reach your goals.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🕒</div>
                    <h3>Flexible Hours</h3>
                    <p>Open 24/7 to accommodate your schedule, because dedication knows no time.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🤝</div>
                    <h3>Community Support</h3>
                    <p>Join a passionate community that will motivate and inspire your fitness journey.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="programs" class="programs">
        <div class="container">
            <h2 class="section-title">OUR ELITE PROGRAMS</h2>
            
            <div class="program-grid">
                {classes_html}
            </div>
        </div>
    </section>

    <section class="cta">
        <div class="container">
            <div class="cta-content">
                <h2>Ready to Transform Your Life?</h2>
                <p>Join Olympus Strength today and start your journey towards a stronger, godlike physique.</p>
                <a href="/signup" class="btn btn-lg">Join Now</a>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-about">
                    <a href="/" class="footer-logo">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                            <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                        </svg>
                        OLYMPUS STRENGTH
                    </a>
                    <p>Forge your legacy at Olympus Strength. We provide the tools, knowledge, and community you need to reach your fitness goals.</p>
                </div>
                
                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/members">Members</a></li>
                        <li><a href="/workouts">Workouts</a></li>
                        <li><a href="/login">Login</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Programs</h4>
                    <ul>
                        <li><a href="#">Olympic Weightlifting</a></li>
                        <li><a href="#">Spartan HIIT</a></li>
                        <li><a href="#">Strength Foundations</a></li>
                        <li><a href="#">All Programs</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Contact Us</h4>
                    <ul>
                        <li>📞 (555) 123-4567</li>
                        <li>📧 info@olympusstrength.com</li>
                        <li>📍 123 Fitness Ave, Olympia</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2025 Olympus Strength. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/home.js"></script>
</body>
</html>""")
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
        
        # Generate member HTML
        members_html = ""
        for member in members:
            members_html += f"""
            <div class="member-card">
                <div class="member-avatar">
                    <i>👤</i>
                </div>
                <div class="member-info">
                    <h3 class="member-name">{member.name}</h3>
                    <div class="member-detail">
                        <i>📧</i> {member.email}
                    </div>
                    <div class="member-detail">
                        <i>🏅</i> {member.membership_type} Membership
                    </div>
                    <div class="member-actions">
                        <button class="btn btn-sm btn-outline">Message</button>
                        <button class="btn btn-sm">Follow</button>
                    </div>
                </div>
            </div>
            """
    
        # If no members found
        if not members_html:
            members_html = "<p>No members found. Be the first to join!</p>"

        # Render login/signup buttons based on authentication status
        auth_buttons = '<a href="/login" class="nav-link">Login</a><a href="/signup" class="btn">Join Now</a>'
        if current_user:
            auth_buttons = f'<a href="/profile" class="nav-link">Profile</a><a href="/logout" class="nav-link">Logout</a>'

        return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Members - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <header>
        <div class="container header-container">
            <a href="/" class="logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </a>
            
            <button class="mobile-toggle">☰</button>
            
            <nav class="nav">
                <a href="/" class="nav-link">Home</a>
                <a href="/members" class="nav-link">Members</a>
                <a href="/workouts" class="nav-link">Workouts</a>
                {auth_buttons}
            </nav>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1 class="page-title">Our Members</h1>
            <p>Meet the Olympians who are forging their legacy with us</p>
        </div>
    </section>

    <section class="members-container">
        <div class="container">
            <div class="search-container">
                <div class="search-box">
                    <input type="text" class="search-input" placeholder="Search members...">
                    <button class="search-btn">🔍</button>
                </div>
            </div>
            
            <div class="members-grid">
                {members_html}
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-about">
                    <a href="/" class="footer-logo">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                            <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                        </svg>
                        OLYMPUS STRENGTH
                    </a>
                    <p>Forge your legacy at Olympus Strength. We provide the tools, knowledge, and community you need to reach your fitness goals.</p>
                </div>
                
                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/members">Members</a></li>
                        <li><a href="/workouts">Workouts</a></li>
                        <li><a href="/login">Login</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Programs</h4>
                    <ul>
                        <li><a href="#">Olympic Weightlifting</a></li>
                        <li><a href="#">Spartan HIIT</a></li>
                        <li><a href="#">Strength Foundations</a></li>
                        <li><a href="#">All Programs</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Contact Us</h4>
                    <ul>
                        <li>📞 (555) 123-4567</li>
                        <li>📧 info@olympusstrength.com</li>
                        <li>📍 123 Fitness Ave, Olympia</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2025 Olympus Strength. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/members.js"></script>
</body>
</html>""")
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

# Workouts page
@app.get("/workouts", response_class=HTMLResponse)
async def get_workouts_page(request: Request, db: Session = Depends(get_db)):
    try:
        workouts = crud.get_workouts(db)
        current_user = await get_optional_user(request, db)
        
        # Generate workout HTML
        workouts_html = ""
        for workout in workouts:
            workouts_html += f"""
            <div class="workout-card">
                <div class="workout-header">
                    <h3>{workout.name}</h3>
                    <span class="workout-badge">{workout.difficulty}</span>
                </div>
                <div class="workout-content">
                    <p>{workout.description}</p>
                    <div class="workout-meta">
                        <span><i>⏱️</i> {workout.duration} min</span>
                        <span><i>🔥</i> {workout.calories} calories</span>
                    </div>
                    <a href="/workouts/{workout.id}" class="btn">View Details</a>
                </div>
            </div>
            """
        
        # If no workouts found
        if not workouts_html:
            workouts_html = """
            <div class="workout-card">
                <div class="workout-header">
                    <h3>Olympian Strength Circuit</h3>
                    <span class="workout-badge">Advanced</span>
                </div>
                <div class="workout-content">
                    <p>Build strength like a god with this challenging full-body circuit designed to push your limits.</p>
                    <div class="workout-meta">
                        <span><i>⏱️</i> 45 min</span>
                        <span><i>🔥</i> 550 calories</span>
                    </div>
                    <a href="#" class="btn">View Details</a>
                </div>
            </div>
            
            <div class="workout-card">
                <div class="workout-header">
                    <h3>Spartan Warrior HIIT</h3>
                    <span class="workout-badge">Intermediate</span>
                </div>
                <div class="workout-content">
                    <p>High-intensity interval training inspired by warrior conditioning to maximize calorie burn and improve conditioning.</p>
                    <div class="workout-meta">
                        <span><i>⏱️</i> 30 min</span>
                        <span><i>🔥</i> 400 calories</span>
                    </div>
                    <a href="#" class="btn">View Details</a>
                </div>
            </div>
            
            <div class="workout-card">
                <div class="workout-header">
                    <h3>Foundations of Power</h3>
                    <span class="workout-badge">Beginner</span>
                </div>
                <div class="workout-content">
                    <p>Master the fundamental movements that build the foundation for legendary strength and power.</p>
                    <div class="workout-meta">
                        <span><i>⏱️</i> 40 min</span>
                        <span><i>🔥</i> 320 calories</span>
                    </div>
                    <a href="#" class="btn">View Details</a>
                </div>
            </div>
            """
        
        # Render login/signup buttons based on authentication status
        auth_buttons = '<a href="/login" class="nav-link">Login</a><a href="/signup" class="btn">Join Now</a>'
        if current_user:
            auth_buttons = f'<a href="/profile" class="nav-link">Profile</a><a href="/logout" class="nav-link">Logout</a>'
        
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workouts - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <header>
        <div class="container header-container">
            <a href="/" class="logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </a>
            
            <button class="mobile-toggle">☰</button>
            
            <nav class="nav">
                <a href="/" class="nav-link">Home</a>
                <a href="/members" class="nav-link">Members</a>
                <a href="/workouts" class="nav-link">Workouts</a>
                {auth_buttons}
            </nav>
        </div>
    </header>

    <section class="page-header">
        <div class="container">
            <h1 class="page-title">Workouts</h1>
            <p>Find your perfect training program to forge your legacy</p>
        </div>
    </section>

    <section class="workouts-container">
        <div class="container">
            <div class="workout-filters">
                <button class="filter-btn active">All</button>
                <button class="filter-btn">Beginner</button>
                <button class="filter-btn">Intermediate</button>
                <button class="filter-btn">Advanced</button>
                <button class="filter-btn">Strength</button>
                <button class="filter-btn">Cardio</button>
                <button class="filter-btn">Flexibility</button>
            </div>
            
            <div class="workouts-list">
                {workouts_html}
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-about">
                    <a href="/" class="footer-logo">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                            <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                        </svg>
                        OLYMPUS STRENGTH
                    </a>
                    <p>Forge your legacy at Olympus Strength. We provide the tools, knowledge, and community you need to reach your fitness goals.</p>
                </div>
                
                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/members">Members</a></li>
                        <li><a href="/workouts">Workouts</a></li>
                        <li><a href="/login">Login</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Programs</h4>
                    <ul>
                        <li><a href="#">Olympic Weightlifting</a></li>
                        <li><a href="#">Spartan HIIT</a></li>
                        <li><a href="#">Strength Foundations</a></li>
                        <li><a href="#">All Programs</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Contact Us</h4>
                    <ul>
                        <li>📞 (555) 123-4567</li>
                        <li>📧 info@olympusstrength.com</li>
                        <li>📍 123 Fitness Ave, Olympia</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2025 Olympus Strength. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/workouts.js"></script>
</body>
</html>""")
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
        user_workouts = crud.get_user_workouts(db, current_user.id)
        
        # Generate workouts HTML
        workouts_html = ""
        for workout in user_workouts:
            workouts_html += f"""
            <div class="completed-workout">
                <div class="workout-info">
                    <h4>{workout.workout_name}</h4>
                    <p>Completed: {workout.date_completed.strftime('%Y-%m-%d')}</p>
                </div>
                <div class="workout-stats">
                    <span><i>⏱️</i> {workout.duration} min</span>
                    <span><i>🔥</i> {workout.calories} cal</span>
                </div>
            </div>
            """
        
        if not workouts_html:
            workouts_html = "<p class='no-data'>No completed workouts yet. Start your fitness journey today!</p>"
        
        # User stats
        total_workouts = len(user_workouts)
        total_minutes = sum(workout.duration for workout in user_workouts) if user_workouts else 0
        total_calories = sum(workout.calories for workout in user_workouts) if user_workouts else 0
        
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Profile - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <header>
        <div class="container header-container">
            <a href="/" class="logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </a>
            
            <button class="mobile-toggle">☰</button>
            
            <nav class="nav">
                <a href="/" class="nav-link">Home</a>
                <a href="/members" class="nav-link">Members</a>
                <a href="/workouts" class="nav-link">Workouts</a>
                <a href="/profile" class="nav-link">Profile</a>
                <a href="/logout" class="nav-link">Logout</a>
            </nav>
        </div>
    </header>

    <section class="profile-container">
        <div class="container">
            <div class="profile-header">
                <div class="profile-avatar">
                    👤
                </div>
                
                <div class="profile-info">
                    <h1 class="profile-name">{current_user.name}</h1>
                    <p class="profile-detail"><i>📧</i> {current_user.email}</p>
                    <p class="profile-detail"><i>📅</i> Member since {current_user.created_at.strftime('%B %Y')}</p>
                    <span class="profile-membership">{current_user.membership_type} Membership</span>
                    
                    <div class="profile-actions">
                        <a href="#" class="btn btn-outline btn-sm">Edit Profile</a>
                        <a href="#" class="btn btn-sm">Track Workout</a>
                    </div>
                </div>
            </div>
            
            <div class="profile-grid">
                <div class="profile-stats">
                    <h2 class="section-title">Stats</h2>
                    
                    <div class="stat-card">
                        <div class="stat-value">{total_workouts}</div>
                        <div class="stat-label">Workouts Completed</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">{total_minutes}</div>
                        <div class="stat-label">Total Minutes</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">{total_calories}</div>
                        <div class="stat-label">Calories Burned</div>
                    </div>
                </div>
                
                <div class="profile-activity">
                    <h2 class="section-title">Recent Activity</h2>
                    
                    <div class="recent-workouts">
                        {workouts_html}
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-about">
                    <a href="/" class="footer-logo">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                            <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                        </svg>
                        OLYMPUS STRENGTH
                    </a>
                    <p>Forge your legacy at Olympus Strength. We provide the tools, knowledge, and community you need to reach your fitness goals.</p>
                </div>
                
                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/members">Members</a></li>
                        <li><a href="/workouts">Workouts</a></li>
                        <li><a href="/login">Login</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Programs</h4>
                    <ul>
                        <li><a href="#">Olympic Weightlifting</a></li>
                        <li><a href="#">Spartan HIIT</a></li>
                        <li><a href="#">Strength Foundations</a></li>
                        <li><a href="#">All Programs</a></li>
                    </ul>
                </div>
                
                <div class="footer-links">
                    <h4>Contact Us</h4>
                    <ul>
                        <li>📞 (555) 123-4567</li>
                        <li>📧 info@olympusstrength.com</li>
                        <li>📍 123 Fitness Ave, Olympia</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2025 Olympus Strength. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/profile.js"></script>
</body>
</html>""")
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
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-form">
            <div class="auth-logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </div>
            
            <h1 class="auth-title">Welcome Back</h1>
            
            <form action="/login" method="post">
                <div class="form-group">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" name="username" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>
                
                <button type="submit" class="btn">Login</button>
            </form>
            
            <div class="auth-footer">
                <p>Don't have an account? <a href="/signup">Sign up</a></p>
                <p><a href="/forgot-password">Forgot your password?</a></p>
            </div>
        </div>
    </div>
</body>
</html>""")

# Login post
@app.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        return HTMLResponse(
            content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Failed - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-form">
            <div class="auth-logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </div>
            
            <h1 class="auth-title">Login Failed</h1>
            
            <div class="error-message">
                <p>Invalid email or password. Please try again.</p>
            </div>
            
            <form action="/login" method="post">
                <div class="form-group">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" name="username" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>
                
                <button type="submit" class="btn">Login</button>
            </form>
            
            <div class="auth-footer">
                <p>Don't have an account? <a href="/signup">Sign up</a></p>
                <p><a href="/forgot-password">Forgot your password?</a></p>
            </div>
        </div>
    </div>
</body>
</html>""",
            status_code=401
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return RedirectResponse(url="/", status_code=303)

# Signup page
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-form">
            <div class="auth-logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </div>
            
            <h1 class="auth-title">Join The Olympians</h1>
            
            <form action="/signup" method="post">
                <div class="form-group">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" id="name" name="name" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" name="email" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="confirm_password" class="form-label">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Membership Type</label>
                    <div class="membership-options">
                        <div class="membership-option">
                            <input type="radio" id="bronze" name="membership_type" value="Bronze" checked>
                            <label for="bronze">Bronze - $29.99/month</label>
                        </div>
                        <div class="membership-option">
                            <input type="radio" id="silver" name="membership_type" value="Silver">
                            <label for="silver">Silver - $49.99/month</label>
                        </div>
                        <div class="membership-option">
                            <input type="radio" id="gold" name="membership_type" value="Gold">
                            <label for="gold">Gold - $79.99/month</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">Sign Up</button>
            </form>
            
            <div class="auth-footer">
                <p>Already have an account? <a href="/login">Login</a></p>
            </div>
        </div>
    </div>
</body>
</html>""")

# Signup post
@app.post("/signup")
async def signup(
    response: Response,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    membership_type: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if passwords match
    if password != confirm_password:
        return HTMLResponse(
            content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signup Failed - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-form">
            <div class="auth-logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </div>
            
            <h1 class="auth-title">Signup Failed</h1>
            
            <div class="error-message">
                <p>Passwords do not match. Please try again.</p>
            </div>
            
            <form action="/signup" method="post">
                <div class="form-group">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" id="name" name="name" class="form-control" required value="{name}">
                </div>
                
                <div class="form-group">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" name="email" class="form-control" required value="{email}">
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="confirm_password" class="form-label">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Membership Type</label>
                    <div class="membership-options">
                        <div class="membership-option">
                            <input type="radio" id="bronze" name="membership_type" value="Bronze" {' checked' if membership_type == 'Bronze' else ''}>
                            <label for="bronze">Bronze - $29.99/month</label>
                        </div>
                        <div class="membership-option">
                            <input type="radio" id="silver" name="membership_type" value="Silver" {' checked' if membership_type == 'Silver' else ''}>
                            <label for="silver">Silver - $49.99/month</label>
                        </div>
                        <div class="membership-option">
                            <input type="radio" id="gold" name="membership_type" value="Gold" {' checked' if membership_type == 'Gold' else ''}>
                            <label for="gold">Gold - $79.99/month</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">Sign Up</button>
            </form>
            
            <div class="auth-footer">
                <p>Already have an account? <a href="/login">Login</a></p>
            </div>
        </div>
    </div>
</body>
</html>""",
            status_code=400
        )
    
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, email)
    if existing_user:
        return HTMLResponse(
            content=f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signup Failed - Olympus Strength</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-form">
            <div class="auth-logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#4CAF50" width="24" height="24">
                    <path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z"/>
                </svg>
                OLYMPUS STRENGTH
            </div>
            
            <h1 class="auth-title">Signup Failed</h1>
            
            <div class="error-message">
                <p>Email already registered. Please use a different email or login.</p>
            </div>
            
            <form action="/signup" method="post">
                <div class="form-group">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" id="name" name="name" class="form-control" required value="{name}">
                </div>
                
                <div class="form-group">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" name="email" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="confirm_password" class="form-label">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Membership Type</label>
                    <div class="membership-options">
                        <div class="membership-option">
                            <input type="radio" id="bronze" name="membership_type" value="Bronze" {' checked' if membership_type == 'Bronze' else ''}>
                            <label for="bronze">Bronze - $29.99/month</label>
                        </div>
                        <div class="membership-option">
                            <input type="radio" id="silver" name="membership_type" value="Silver" {' checked' if membership_type == 'Silver' else ''}>
                            <label for="silver">Silver - $49.99/month</label>
                        </div>
                        <div class="membership-option">
                            <input type="radio" id="gold" name="membership_type" value="Gold" {' checked' if membership_type == 'Gold' else ''}>
                            <label for="gold">Gold - $79.99/month</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">Sign Up</button>
            </form>
            
            <div class="auth-footer">
                <p>Already have an account? <a href="/login">Login</a></p>
            </div>
        </div>
    </div>
</body>
</html>""",
            status_code=400
        )
    
    # Create user
    hashed_password = get_password_hash(password)
    user = crud.create_user(db, schemas.UserCreate(
        name=name,
        email=email,
        password=hashed_password,
        membership_type=membership_type
    ))
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return RedirectResponse(url="/", status_code=303)

# Logout
@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return RedirectResponse(url="/", status_code=303)

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

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)