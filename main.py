from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
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

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Serve the simple HTML page directly
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        # Read the HTML file content
        html_file_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        
        if os.path.exists(html_file_path):
            with open(html_file_path, "r") as file:
                html_content = file.read()
            return HTMLResponse(content=html_content)
        else:
            # If file doesn't exist, return a simple HTML
            return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Olympus Strength</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #4CAF50;
        }
        .nav {
            margin-bottom: 20px;
        }
        .nav a {
            margin-right: 10px;
            color: #4CAF50;
            text-decoration: none;
        }
        .btn {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/members">Members</a>
        <a href="/workouts">Workouts</a>
        <a href="/login">Login</a>
    </div>
    
    <h1>Olympus Strength</h1>
    <p>Welcome to Olympus Strength. Our main application is being updated.</p>
    <p>Please check back soon for our fully functioning fitness platform.</p>
    <a href="/members" class="btn">Join Now</a>
</body>
</html>
            """)
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
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .error {
            color: #F44336;
        }
    </style>
</head>
<body>
    <h1 class="error">Internal Server Error</h1>
    <p>We're sorry, something went wrong on our end. Please try again later.</p>
    <p>Error details: {str(e)}</p>
</body>
</html>
        """)

# Members page (simple version)
@app.get("/members", response_class=HTMLResponse)
async def get_members_page(request: Request, db: Session = Depends(get_db)):
    try:
        members = crud.get_members(db)
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Members - Olympus Strength</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #4CAF50;
        }}
        .nav {{
            margin-bottom: 20px;
        }}
        .nav a {{
            margin-right: 10px;
            color: #4CAF50;
            text-decoration: none;
        }}
        .member-card {{
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        form {{
            margin-top: 30px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 4px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
        }}
        input, select {{
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        button {{
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/members">Members</a>
        <a href="/workouts">Workouts</a>
        <a href="/login">Login</a>
    </div>
    
    <h1>Our Members</h1>
    
    <div class="members-list">
        {
            ''.join([f"""
            <div class="member-card">
                <h3>{member.name}</h3>
                <p>Email: {member.email}</p>
                <p>Membership: {member.membership_type}</p>
            </div>
            """ for member in members]) if members else '<p>No members found.</p>'
        }
    </div>
    
    <form id="member-form">
        <h2>Join Our Community</h2>
        <div>
            <label for="name">Full Name</label>
            <input type="text" id="name" name="name" required>
        </div>
        <div>
            <label for="email">Email Address</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div>
            <label for="membership">Membership Type</label>
            <select id="membership" name="membership_type" required>
                <option value="" disabled selected>Choose your membership</option>
                <option value="Basic">Basic - $29.99/month</option>
                <option value="Standard">Standard - $49.99/month</option>
                <option value="Premium">Premium - $79.99/month</option>
                <option value="Elite">Elite - $99.99/month</option>
            </select>
        </div>
        <button type="submit">Become a Member</button>
    </form>
    
    <script>
        document.getElementById('member-form').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const formData = {{
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                membership_type: document.getElementById('membership').value
            }};
            
            try {{
                const response = await fetch('/api/members', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(formData)
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    alert('Membership created successfully!');
                    window.location.reload();
                }} else {{
                    alert('Error: ' + (data.detail || 'Failed to create membership'));
                }}
            }} catch (error) {{
                alert('Error: ' + error.message);
            }}
        }});
    </script>
</body>
</html>
        """)
    except Exception as e:
        logger.error(f"Error rendering members page: {e}")
        return HTMLResponse(content="<p>Error loading members page</p>")

# API endpoint for creating members
@app.post("/api/members", response_model=schemas.Member)
def create_member_api(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    db_member = crud.get_member_by_email(db, email=member.email)
    if db_member:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_member(db=db, member=member)

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