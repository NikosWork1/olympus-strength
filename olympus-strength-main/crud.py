from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime
from passlib.context import CryptContext

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
    hashed_password = pwd_context.hash(member.password)
    db_member = models.Member(
        name=member.name,
        email=member.email,
        password_hash=hashed_password,
        phone=member.phone,
        membership_type=member.membership_type,
        role=member.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_member(db: Session, member_id: int, member: schemas.MemberUpdate):
    db_member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if db_member:
        update_data = member.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password" and value:
                value = pwd_context.hash(value)
                key = "password_hash"
            setattr(db_member, key, value)
        db.commit()
        db.refresh(db_member)
    return db_member

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
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout:
        update_data = workout.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_workout, key, value)
        db.commit()
        db.refresh(db_workout)
    return db_workout

def delete_workout(db: Session, workout_id: int):
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout:
        db.delete(db_workout)
        db.commit()
        return True
    return False

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
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

def get_member_bookings(db: Session, member_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).filter(models.Booking.member_id == member_id).offset(skip).limit(limit).all()

def get_class_bookings(db: Session, class_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).filter(models.Booking.class_id == class_id).offset(skip).limit(limit).all()

def create_booking(db: Session, booking: schemas.BookingCreate):
    if booking.class_date is None:
        # If no specific date, use current date/time
        booking.class_date = datetime.now()
        
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

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

def create_member_workout(db: Session, member_workout: schemas.MemberWorkoutCreate):
    db_member_workout = models.MemberWorkout(**member_workout.dict())
    db.add(db_member_workout)
    db.commit()
    db.refresh(db_member_workout)
    return db_member_workout

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