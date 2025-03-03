from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.orm import relationship
import datetime
from database import Base

# Association table for many-to-many relationships
class_member_association = Table(
    'class_member_association', 
    Base.metadata,
    Column('member_id', Integer, ForeignKey('members.id')),
    Column('class_id', Integer, ForeignKey('classes.id'))
)

class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255))  # Hashed password
    phone = Column(String(20))
    membership_type = Column(String(50), nullable=False)
    join_date = Column(DateTime, default=datetime.datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bookings = relationship("Booking", back_populates="member")
    classes = relationship("GymClass", secondary=class_member_association, back_populates="members")
    workouts = relationship("MemberWorkout", back_populates="member")

class GymClass(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    instructor = Column(String(100))
    schedule = Column(String(255))
    level = Column(String(50))
    max_capacity = Column(Integer, default=20)
    
    # Relationships
    bookings = relationship("Booking", back_populates="gym_class")
    members = relationship("Member", secondary=class_member_association, back_populates="classes")

class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(String(50))
    category = Column(String(50))
    duration = Column(Integer, default=45)  # Add this line
    calories = Column(Integer, default=300)  # Add this line
    
    # Relationships
    member_workouts = relationship("MemberWorkout", back_populates="workout")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    booking_date = Column(DateTime, default=datetime.datetime.now)
    class_date = Column(DateTime)
    status = Column(String(50), default="confirmed")  # confirmed, cancelled, attended
    
    # Relationships
    member = relationship("Member", back_populates="bookings")
    gym_class = relationship("GymClass", back_populates="bookings")

class MemberWorkout(Base):
    __tablename__ = "member_workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    date_assigned = Column(DateTime, default=datetime.datetime.now)
    completion_status = Column(String(50), default="assigned")  # assigned, in_progress, completed
    notes = Column(Text)
    
    # Relationships
    member = relationship("Member", back_populates="workouts")
    workout = relationship("Workout", back_populates="member_workouts")