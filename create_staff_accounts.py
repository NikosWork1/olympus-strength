"""
Script to create pre-defined coach and admin accounts.
Run this script once after setting up the database to create the staff accounts.
"""

import os
import sys
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import crud, schemas
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Staff account data
coaches = [
    {
        "name": "Alex Hermes",
        "email": "alex@olympusstrength.com",
        "password": "1234",
        "phone": "+30 210 5555 101",
        "role": "coach"
    },
    {
        "name": "Marcus Leonidas",
        "email": "marcus@olympusstrength.com",
        "password": "1234",
        "phone": "+30 210 5555 102",
        "role": "coach"
    },
    {
        "name": "Helena Troy",
        "email": "helena@olympusstrength.com", 
        "password": "1234",
        "phone": "+30 210 5555 103",
        "role": "coach"
    },
    {
        "name": "Diana Artemis",
        "email": "diana@olympusstrength.com",
        "password": "1234",
        "phone": "+30 210 5555 104", 
        "role": "coach"
    },
    {
        "name": "Jason Argos",
        "email": "jason@olympusstrength.com",
        "password": "1234",
        "phone": "+30 210 5555 105",
        "role": "coach"
    }
]

admin = {
    "name": "Zeus Olympian",
    "email": "admin@olympusstrength.com",
    "password": "adminadmin",
    "phone": "+30 210 5555 100",
    "role": "admin"
}

def create_staff_accounts():
    db = SessionLocal()
    try:
        # Create coach accounts
        for coach_data in coaches:
            # Check if account already exists
            existing_coach = crud.get_member_by_email(db, coach_data["email"])
            if existing_coach:
                print(f"Coach {coach_data['name']} already exists.")
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
            print(f"Created coach account: {db_coach.name} ({db_coach.email})")
        
        # Create admin account
        existing_admin = crud.get_member_by_email(db, admin["email"])
        if existing_admin:
            print(f"Admin {admin['name']} already exists.")
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
            print(f"Created admin account: {db_admin.name} ({db_admin.email})")
            
        print("\nStaff accounts created successfully!")
        print("\nCoach login credentials:")
        for coach in coaches:
            print(f"- {coach['name']}: {coach['email']} / {coach['password']}")
        
        print("\nAdmin login credentials:")
        print(f"- {admin['name']}: {admin['email']} / {admin['password']}")
            
    except Exception as e:
        print(f"Error creating staff accounts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_staff_accounts()