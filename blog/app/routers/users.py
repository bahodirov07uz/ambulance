# === routers/user.py ===
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import schemas
from app.models import models
from app.services.dependencies import get_current_active_user,get_db
from app.crud import crud

router = APIRouter()

@router.get("/users/", response_model=List[schemas.UserOut])
async def read_users(skip: int = 0, limit: int = 100,
                     current_user: models.User = Depends(get_current_active_user),
                     db: AsyncSession = Depends(get_db)):
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Yetarli ruxsatlar yo'q")
    return await crud.get_users(db, skip=skip, limit=limit)

