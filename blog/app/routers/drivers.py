from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.schemas import DriverCreate, DriverOut, DriverUpdateLocation
from app.services.dependencies import get_db
from ..crud import crud
from ..crud.driver import create_driver
router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("/", response_model=DriverOut)
async def register_driver(driver: DriverCreate, db: AsyncSession = Depends(get_db)):
    return await create_driver(db, driver)


