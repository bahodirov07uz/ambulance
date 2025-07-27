from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.sql import func
import enum

class UserRole(enum.Enum):  # str dan emas, enum.Enum dan meros oling
    SUPERADMIN = "superadmin"
    HOSPITAL_ADMIN = "hospital_admin"
    USER = "user"
    DRIVER = "driver"
    
class RequestStatus(enum.Enum):  # Bu ham xuddi shunday
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    drivers = relationship("Driver", back_populates="hospital")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    locations = relationship("Location", back_populates="user")

    emergency_requests = relationship(
        "EmergencyRequest",
        back_populates="user",
        foreign_keys="EmergencyRequest.user_id"
    )

    driver_requests = relationship(
        "EmergencyRequest",
        back_populates="driver",
        foreign_keys="EmergencyRequest.driver_id"
    )

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    car_number = Column(String, nullable=False)
    car_type = Column(String)
    phone_number = Column(String)
    is_available = Column(Boolean, default=False)

    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))

    user = relationship("User", backref="driver_profile")
    hospital = relationship("Hospital", back_populates="drivers")

class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)
    status = Column(Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="emergency_requests", foreign_keys=[user_id])
    driver = relationship("User", back_populates="driver_requests", foreign_keys=[driver_id])
    hospital = relationship("Hospital")

class PhoneVerificationCode(Base):
    __tablename__ = "phone_verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    code = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="locations")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", foreign_keys=[user_id])
    driver = relationship("User", foreign_keys=[driver_id])