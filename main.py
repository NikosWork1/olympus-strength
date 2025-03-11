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
 
 # The @app.get("/login") route for rendering the login page
 # Login page
 @app.get("/login", response_class=HTMLResponse)
 async def login_page(request: Request):
     return templates.TemplateResponse("login.html", {"request": request})
 
 # The @app.post("/login") route for handling form submission
 # Login post
 @app.post("/login")
 async def login(
     response: Response,
     request: Request,
     form_data: OAuth2PasswordRequestForm = Depends(),
     db: Session = Depends(get_db)
 ):
     # Attempt to authenticate the user
     member = crud.get_member_by_email(db, form_data.username)
     if not member or not verify_password(form_data.password, member.password_hash):
         # Return to login page with error if authentication fails
         return templates.TemplateResponse(
             "login.html", 
             {
                 "request": request,
                 "request": {"method": "GET"},
                 "error": "Invalid email or password"
             },
             status_code=401
         )
 
     # Create access token with user role included
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
         data={"sub": member.email, "role": member.role}, 
         expires_delta=access_token_expires
         data={"sub": member.email, "role": member.role}, expires_delta=access_token_expires
     )
 
     # Set cookie and redirect to home page
     # Set cookie and redirect
     response = RedirectResponse(url="/", status_code=303)
     response.set_cookie(
         key="access_token",
 @@ -1060,49 +1136,6 @@
             "error_message": "There was an error loading your bookings. Please try again later.",
             "current_user": current_user
         })
     
 # About page
 @app.get("/about", response_class=HTMLResponse)
 async def about_page(request: Request, db: Session = Depends(get_db)):
     try:
         current_user = await get_optional_user(request, db)
         return templates.TemplateResponse("about.html", {
             "request": request,
             "current_user": current_user,
             "title": "About Us"
         })
     except Exception as e:
         logger.error(f"Error rendering about page: {e}")
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
     
     
 # Run the app
 if __name__ == "__main__":
     import uvicorn
