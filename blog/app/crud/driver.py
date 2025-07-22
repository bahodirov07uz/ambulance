from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import Driver, EmergencyRequest, RequestStatus, User
from ..schemas.schemas import DriverCreate, EmergencyRequestCreate
from datetime import datetime


async def create_driver(db: AsyncSession, data: DriverCreate):
    driver = Driver(**data.dict())
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    result = await db.execute(select(User).where(User.id == driver.user_id))
    user = result.scalar_one_or_none()

    if user:
        user.role = "driver"
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return driver

