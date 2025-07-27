from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import Hospital
from app.schemas.schemas import HospitalCreate

async def create_hospital(db: AsyncSession, data: HospitalCreate):
    hospital = Hospital(**data.dict())
    db.add(hospital)
    await db.commit()
    await db.refresh(hospital)
    return hospital
 
async def get_all_hospitals(db:AsyncSession):
    result = await db.execute(select(Hospital))
    return result.scalars().all()