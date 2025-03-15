from datetime import datetime
from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Member CRUD operations ---
def get_member(db: Session, member_id: int):
    return db.query(models.Member).filter(models.Member.id == member_id).first()

def get_member_by_email(db: Session, email: str):
    return db.query(models.Member).filter(models.Member.email == email).first()

def get_members(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Member).offset(skip).limit(limit).all()

def create_member(db: Session, member: schemas.MemberCreate):
    try:
        # Hash the password
        hashed_password = pwd_context.hash(member.password)
        
        # Create the member object
        db_member = models.Member(
            name=member.name,
            email=member.email,
            password_hash=hashed_password,
            phone=member.phone,
            membership_type=member.membership_type,
            role=member.role,
            join_date=datetime.now(),
            is_active=True
        )
        
        # Add member to database
        db.add(db_member)
        db.commit()
        db.refresh(db_member)

        # Create initial membership transaction
        membership_prices = {
            "Bronze": 29.99,
            "Silver": 49.99,
            "Gold": 79.99
        }
        
        if member.membership_type in membership_prices:
            transaction = models.Transaction(
                member_id=db_member.id,
                amount=membership_prices[member.membership_type],
                type="Membership Fee",
                description=f"Initial {member.membership_type} membership subscription",
                status="completed",
                date=datetime.now()
            )
            db.add(transaction)
            db.commit()

        return db_member
    except Exception as e:
        db.rollback()
        logger.error(f"Database error creating member: {e}")
        raise e

def update_member(db: Session, member_id: int, member: schemas.MemberUpdate):
    try:
        db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
        if db_member:
            # Store the old membership type
            old_membership_type = db_member.membership_type
            
            # Update member data
            update_data = member.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key == "password" and value:
                    value = pwd_context.hash(value)
                    key = "password_hash"
                setattr(db_member, key, value)
            
            # If membership type changed, create a new transaction
            if "membership_type" in update_data and old_membership_type != update_data["membership_type"]:
                membership_prices = {
                    "Bronze": 29.99,
                    "Silver": 49.99,
                    "Gold": 79.99
                }
                
                if update_data["membership_type"] in membership_prices:
                    transaction = models.Transaction(
                        member_id=member_id,
                        amount=membership_prices[update_data["membership_type"]],
                        type="Membership Fee",
                        description=f"Membership upgrade from {old_membership_type} to {update_data['membership_type']}",
                        status="completed",
                        date=datetime.now()
                    )
                    db.add(transaction)
            
            db.commit()
            db.refresh(db_member)
        return db_member
    except Exception as e:
        db.rollback()
        logger.error(f"Database error updating member: {e}")
        raise e

def delete_member(db: Session, member_id: int):
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if db_member:
        db.delete(db_member)
        db.commit()
        return True
    return False

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_member(db: Session, email: str, password: str):
    member = get_member_by_email(db, email)
    if not member:
        return False
    if not verify_password(password, member.password_hash):
        return False
    return member

# --- Workout CRUD operations ---
def get_workout(db: Session, workout_id: int):
    return db.query(models.Workout).filter(models.Workout.id == workout_id).first()

def get_workouts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Workout).offset(skip).limit(limit).all()

def create_workout(db: Session, workout: schemas.WorkoutCreate):
    db_workout = models.Workout(**workout.dict())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

def update_workout(db: Session, workout_id: int, workout: schemas.WorkoutUpdate):
    try:
        db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
        if db_workout is None:
            return None
            
        # Update only the fields that are provided
        update_data = workout.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_workout, key, value)
            
        db.commit()
        db.refresh(db_workout)
        return db_workout
    except Exception as e:
        db.rollback()
        logger.error(f"Database error updating workout: {e}")
        raise e


def delete_workout(db: Session, workout_id: int):
    try:
        db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
        if not db_workout:
            return False
            
        # Check for associated records first
        workout_used = db.query(models.MemberWorkout).filter(
            models.MemberWorkout.workout_id == workout_id
        ).first()
        
        if workout_used:
            # If it's being used, we should handle this gracefully
            # For example, we could mark it as inactive instead of deleting
            db_workout.is_active = False
            db.commit()
            return True
            
        # If not used, we can safely delete
        db.delete(db_workout)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Database error deleting workout: {e}")
        raise e

# --- GymClass CRUD operations ---
def get_class(db: Session, class_id: int):
    return db.query(models.GymClass).filter(models.GymClass.id == class_id).first()

def get_classes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.GymClass).offset(skip).limit(limit).all()

def create_class(db: Session, gym_class: schemas.GymClassCreate):
    db_class = models.GymClass(**gym_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def update_class(db: Session, class_id: int, gym_class: schemas.GymClassUpdate):
    db_class = db.query(models.GymClass).filter(models.GymClass.id == class_id).first()
    if db_class:
        update_data = gym_class.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_class, key, value)
        db.commit()
        db.refresh(db_class)
    return db_class

def delete_class(db: Session, class_id: int):
    db_class = db.query(models.GymClass).filter(models.GymClass.id == class_id).first()
    if db_class:
        db.delete(db_class)
        db.commit()
        return True
    return False

# --- Booking CRUD operations ---
def get_booking(db: Session, booking_id: int):
    # Join Booking with GymClass to get class details
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    if booking:
        # Get class details
        gym_class = db.query(models.GymClass).filter(models.GymClass.id == booking.class_id).first()
        if gym_class:
            booking.class_name = gym_class.name
            booking.class_instructor = gym_class.instructor
            
    return booking

def get_member_bookings(db: Session, member_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).filter(models.Booking.member_id == member_id).offset(skip).limit(limit).all()

def get_class_bookings(db: Session, class_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).filter(models.Booking.class_id == class_id).offset(skip).limit(limit).all()

def create_booking(db: Session, booking: schemas.BookingCreate):
    """
    Creates a new booking for a member in a specific class at a specific date/time
    
    Args:
        db: Database session
        booking: BookingCreate schema with member_id, class_id, and class_date
        
    Returns:
        Created Booking object
    """
    try:
        # Create the booking with all required fields
        db_booking = models.Booking(
            member_id=booking.member_id,
            class_id=booking.class_id,
            class_date=booking.class_date,
            status="confirmed",
            booking_date=datetime.now()
        )
        
        # Add to database session
        db.add(db_booking)
        
        # Commit the transaction
        db.commit()
        
        # Refresh the model (populates the id field)
        db.refresh(db_booking)
        
        return db_booking
    except Exception as e:
        # In case of error, rollback the transaction
        db.rollback()
        # Re-raise the exception
        raise e

#Cancel booking
def get_booking(db: Session, booking_id: int):
    # Join Booking with GymClass to get class details
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    if booking:
        # Get class details
        gym_class = db.query(models.GymClass).filter(models.GymClass.id == booking.class_id).first()
        if gym_class:
            booking.class_name = gym_class.name
            booking.class_instructor = gym_class.instructor
            
    return booking

def update_booking(db: Session, booking_id: int, booking: schemas.BookingUpdate):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking:
        update_data = booking.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_booking, key, value)
        db.commit()
        db.refresh(db_booking)
    return db_booking

def delete_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return True
    return False

def get_member_bookings(db: Session, member_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).filter(models.Booking.member_id == member_id).offset(skip).limit(limit).all()

def get_class_bookings(db: Session, class_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).filter(models.Booking.class_id == class_id).offset(skip).limit(limit).all()

def create_booking(db: Session, booking: schemas.BookingCreate):
    try:
        db_booking = models.Booking(
            member_id=booking.member_id,
            class_id=booking.class_id,
            class_date=booking.class_date,
            status="confirmed"
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except Exception as e:
        db.rollback()
        logger.error(f"Database error creating booking: {e}")
        raise e

def update_booking(db: Session, booking_id: int, booking: schemas.BookingUpdate):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking:
        update_data = booking.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_booking, key, value)
        db.commit()
        db.refresh(db_booking)
    return db_booking

def delete_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return True
    return False

# --- MemberWorkout CRUD operations ---
def get_member_workout(db: Session, member_workout_id: int):
    return db.query(models.MemberWorkout).filter(models.MemberWorkout.id == member_workout_id).first()

def get_member_workouts(db: Session, member_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.MemberWorkout).filter(models.MemberWorkout.member_id == member_id).offset(skip).limit(limit).all()

# Update these functions in crud.py

def update_workout(db: Session, workout_id: int, workout: schemas.WorkoutUpdate):
    try:
        db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
        if db_workout is None:
            return None
            
        # Update only the fields that are provided
        update_data = workout.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_workout, key, value)
            
        db.commit()
        db.refresh(db_workout)
        return db_workout
    except Exception as e:
        db.rollback()
        logger.error(f"Database error updating workout: {e}")
        raise e

def delete_workout(db: Session, workout_id: int):
    try:
        db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
        if not db_workout:
            return False
            
        # Check for associated records first
        workout_used = db.query(models.MemberWorkout).filter(
            models.MemberWorkout.workout_id == workout_id
        ).first()
        
        if workout_used:
            # If it's being used, we should handle this gracefully
            # For example, we could mark it as inactive instead of deleting
            db_workout.is_active = False
            db.commit()
            return True
            
        # If not used, we can safely delete
        db.delete(db_workout)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Database error deleting workout: {e}")
        raise e

def create_member(db: Session, member: schemas.MemberCreate):
    try:
        # Hash the password
        hashed_password = pwd_context.hash(member.password)
        
        # Create the member object
        db_member = models.Member(
            name=member.name,
            email=member.email,
            password_hash=hashed_password,
            phone=member.phone,
            membership_type=member.membership_type,
            role=member.role,
            join_date=datetime.now(),
            is_active=True
        )
        
        # Add to database
        db.add(db_member)
        db.commit()
        db.refresh(db_member)

        # Create initial membership transaction
        membership_prices = {
            "Bronze": 29.99,
            "Silver": 49.99,
            "Gold": 79.99
        }
        
        if member.membership_type in membership_prices:
            transaction = models.Transaction(
                member_id=db_member.id,
                amount=membership_prices[member.membership_type],
                type="Membership Fee",
                description=f"Initial {member.membership_type} membership subscription",
                status="completed",
                date=datetime.now()
            )
            db.add(transaction)
            db.commit()

        return db_member
    except Exception as e:
        db.rollback()
        logger.error(f"Database error creating member: {e}")
        raise e

def update_member_workout(db: Session, member_workout_id: int, member_workout: schemas.MemberWorkoutUpdate):
    db_member_workout = db.query(models.MemberWorkout).filter(models.MemberWorkout.id == member_workout_id).first()
    if db_member_workout:
        update_data = member_workout.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_member_workout, key, value)
        db.commit()
        db.refresh(db_member_workout)
    return db_member_workout

def delete_member_workout(db: Session, member_workout_id: int):
    db_member_workout = db.query(models.MemberWorkout).filter(models.MemberWorkout.id == member_workout_id).first()
    if db_member_workout:
        db.delete(db_member_workout)
        db.commit()
        return True
    return False


def assign_workout_to_coach(db: Session, workout_id: int, coach_id: int):
    """
    Assign a workout to a specific coach.
    This creates an association between the workout and the coach.
    """
    # First check if the workout exists
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if not workout:
        return False
    
    # Then check if the user is a coach
    coach = db.query(models.Member).filter(
        models.Member.id == coach_id,
        models.Member.role == "coach"
    ).first()
    if not coach:
        return False
    
    # Create coach_workout association (you'll need to add this table to models.py)
    coach_workout = models.CoachWorkout(
        coach_id=coach_id,
        workout_id=workout_id
    )
    
    db.add(coach_workout)
    db.commit()
    db.refresh(coach_workout)
    return coach_workout

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_monthly_revenue(db: Session, year: int =datetime.now().year, month: int = datetime.now().month):
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    result = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.date >= start_date,
        models.Transaction.date < end_date,
        models.Transaction.status == "completed"
    ).scalar()
    
    return result or 0

def get_financial_summary(db: Session, year: int = datetime.now().year, month: int = datetime.now().month):
    try:
        # Get start and end dates for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get all active members for membership stats
        active_members = db.query(models.Member).filter(
            models.Member.is_active == True,
            models.Member.role == "customer"  # Only count customers
        ).all()
        
        # Get membership revenue from transactions
        membership_revenue = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.date >= start_date,
            models.Transaction.date < end_date,
            models.Transaction.status == "completed",
            models.Transaction.type == "Membership Fee"
        ).scalar() or 0
        
        # Get other transactions (e.g., personal training, merchandise)
        other_transactions = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.date >= start_date,
            models.Transaction.date < end_date,
            models.Transaction.status == "completed",
            models.Transaction.type != "Membership Fee"
        ).scalar() or 0
        
        # Total revenue
        revenue = membership_revenue + other_transactions
        
        # Get expenses
        expenses = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.date >= start_date,
            models.Transaction.date < end_date,
            models.Transaction.status == "completed",
            models.Transaction.amount < 0
        ).scalar() or 0
        
        # Calculate membership statistics
        membership_stats = {
            "Bronze": 0,
            "Silver": 0,
            "Gold": 0
        }
        
        for member in active_members:
            if member.membership_type and member.membership_type in membership_stats:
                membership_stats[member.membership_type] += 1
        
        # Calculate growth compared to previous month
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        
        prev_revenue = get_monthly_revenue(db, prev_year, prev_month)
        growth = 0
        if prev_revenue > 0:
            growth = ((revenue - prev_revenue) / prev_revenue) * 100
        
        return {
            "revenue": revenue,
            "expenses": abs(expenses),  # Convert to positive for display
            "net_profit": revenue + expenses,  # expenses are negative
            "growth": growth,
            "membership_revenue": membership_revenue,
            "other_revenue": other_transactions,
            "membership_stats": membership_stats
        }
    except Exception as e:
        logger.error(f"Error in get_financial_summary: {str(e)}")
        return {
            "revenue": 0,
            "expenses": 0,
            "net_profit": 0,
            "growth": 0,
            "membership_revenue": 0,
            "other_revenue": 0,
            "membership_stats": {
                "Bronze": 0,
                "Silver": 0,
                "Gold": 0
            }
        }

