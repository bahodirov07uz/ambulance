from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependecies import get_async_session
from ..crud import hospital as hospital_crud
from ..schemas.schemas import HospitalCreate
from ..models.models import Hospital

router = APIRouter(prefix="/hospitals",tags=["Hospitals"])

@router.post("/", response_model=dict)
async def register_hospital(
    hospital_data: HospitalCreate,
    db: AsyncSession = Depends(get_async_session)
):
    hospital = await hospital_crud.create_hospital(db, hospital_data)
    return {"id": hospital.id, "name": hospital.name}