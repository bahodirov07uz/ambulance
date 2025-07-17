from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import Driver, EmergencyRequest, RequestStatus
from ..schemas.schemas import DriverCreate, EmergencyRequestCreate
from datetime import datetime


async def create_driver(db: AsyncSession, data: DriverCreate):
    driver = Driver(**data.dict())
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver

