from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc
from ..schemas import schemas
from ..models import models
from ..config import pwd_context
from datetime import datetime

# === User CRUD ===

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
        phone_number=user.phone_number
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def verify_code(db: AsyncSession, user_id: int, code: str):
    result = await db.execute(
        select(models.PhoneVerificationCode).where(
            and_(
                models.PhoneVerificationCode.user_id == user_id,
                models.PhoneVerificationCode.code == code,
                models.PhoneVerificationCode.expires_at >= datetime.utcnow()
            )
        )
    )
    verification = result.scalars().first()
    if verification:
        user_result = await db.execute(select(models.User).where(models.User.id == user_id))
        user = user_result.scalars().first()
        if user:
            user.is_verified = True
            await db.commit()
            return True
    return False

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def get_users_by_role(db: AsyncSession, role: str, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.User).where(models.User.role == role).offset(skip).limit(limit)
    )
    return result.scalars().all()

# === Location CRUD ===

async def get_user_locations(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Location)
        .where(models.Location.user_id == user_id)
        .order_by(desc(models.Location.timestamp))
    )
    return result.scalars().all()

async def assign_driver_to_user(db: AsyncSession, user_id: int, driver_id: int):
    assignment = models.Assignment(user_id=user_id, driver_id=driver_id)
    db.add(assignment)
    await db.commit()
    return assignment

async def get_driver_location_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Assignment).where(models.Assignment.user_id == user_id))
    assignment = result.scalars().first()
    if not assignment:
        return None
    location_result = await db.execute(
        select(models.Location)
        .where(models.Location.user_id == assignment.driver_id)
        .order_by(desc(models.Location.timestamp))
    )
    return location_result.scalars().first()

async def update_user_location(db: AsyncSession, user_id: int, location: schemas.LocationUpdate):
    db_location = models.Location(
        user_id=user_id,
        latitude=location.latitude,
        longitude=location.longitude
    )
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location

