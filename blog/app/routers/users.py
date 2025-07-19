# === routers/user.py ===
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import schemas
from app.models import models
from app.services.dependencies import get_current_user,get_db
from app.crud import crud

router = APIRouter()

@router.get("/users/me", response_model=schemas.UserOut)
async def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user
