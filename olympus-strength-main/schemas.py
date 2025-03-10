from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Member Schemas
class MemberBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    membership_type: str
    role: Optional[str] = "customer"

class MemberCreate(MemberBase):
    password: str

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = None
    is_active: Optional[bool] = None

class Member(MemberBase):
    id: int
    join_date: datetime
    is_active: bool
    
    class Config:
        orm_mode = True

# Workout Schemas
class WorkoutBase(BaseModel):
    name: str
    description: str
    difficulty: str
    category: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None

class Workout(WorkoutBase):
    id: int
    
    class Config:
        orm_mode = True

# GymClass Schemas
class GymClassBase(BaseModel):
    name: str
    description: str
    instructor: str
    schedule: str
    level: str
    max_capacity: Optional[int] = 20

class GymClassCreate(GymClassBase):
    pass

class GymClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    schedule: Optional[str] = None
    level: Optional[str] = None
    max_capacity: Optional[int] = None

class GymClass(GymClassBase):
    id: int
    
    class Config:
        orm_mode = True

# Booking Schemas
class BookingBase(BaseModel):
    member_id: int
    class_id: int
    class_date: Optional[datetime] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    class_date: Optional[datetime] = None

class Booking(BookingBase):
    id: int
    booking_date: datetime
    status: str
    
    class Config:
        orm_mode = True

# MemberWorkout Schemas
class MemberWorkoutBase(BaseModel):
    member_id: int
    workout_id: int
    notes: Optional[str] = None

class MemberWorkoutCreate(MemberWorkoutBase):
    pass

class MemberWorkoutUpdate(BaseModel):
    completion_status: Optional[str] = None
    notes: Optional[str] = None

class MemberWorkout(MemberWorkoutBase):
    id: int
    date_assigned: datetime
    completion_status: str
    
    class Config:
        orm_mode = True

# Login Schema
class Login(BaseModel):
    email: EmailStr
    password: str