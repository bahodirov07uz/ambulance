from sqlalchemy.orm import Session
from . import models, schemas
from .config import pwd_context
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
        phone_number=user.phone_number  # agar schemas.UserCreate da mavjud bo‘lsa
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_code(db:Session, user_id:int,code:str):
    verification = db.query(models.PhoneVerificationCode).filter(
        models.PhoneVerificationCode.user_id == user_id,
        models.PhoneVerificationCode.code == code,
        models.PhoneVerificationCode.expires_at >= datetime.utcnow()
    ).first()
    
    if verification:
        user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
        return True
    return False

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_users_by_role(db: Session, role: str, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.role == role).offset(skip).limit(limit).all()

#locations
def get_user_locations(db: Session, user_id: int):
    return db.query(models.Location).filter(models.Location.user_id == user_id).order_by(models.Location.timestamp.desc()).all()
    
def assign_driver_to_user(db: Session, user_id: int, driver_id: int):
    assignment = models.Assignment(user_id=user_id, driver_id=driver_id)
    db.add(assignment)
    db.commit()
    return assignment

def get_driver_location_for_user(db: Session, user_id: int):
    assignment = db.query(models.Assignment).filter_by(user_id=user_id).first()
    if not assignment:
        return None
    latest_location = (
        db.query(models.Location)
        .filter(models.Location.user_id == assignment.driver_id)
        .order_by(models.Location.timestamp.desc())
        .first()
    )
    return latest_location

def update_user_location(db: Session, user_id: int, location: schemas.LocationUpdate):
    db_location = models.Location(
        user_id=user_id,
        latitude=location.latitude,
        longitude=location.longitude
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location