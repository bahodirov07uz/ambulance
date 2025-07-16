from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from jose import JWTError, jwt
from urllib.parse import parse_qs

from app.schemas import schemas
from app.crud import crud
from app.models import models
from app.config import settings
from app.services.dependencies import get_current_active_user, get_db

router = APIRouter(prefix="/location", tags=["Location"])

# WebSocket connectionlar ro'yxati
active_connections: List[WebSocket] = []

@router.post("/update_location")
async def update_location(
    location: schemas.LocationUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await crud.update_user_location(db, current_user.id, location)
    
    for connection in active_connections:
        await connection.send_json({
            "user_id": current_user.id,
            "lat": location.latitude,
            "lng": location.longitude
        })
    
    return {"status": "Location updated"}

@router.websocket("/ws/location")
async def websocket_location(websocket: WebSocket):
    await websocket.accept()
    print("connection open")

    token_query = parse_qs(websocket.url.query).get("token", [None])[0]
    if not token_query:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token_query, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # WebSocketni ochiq tutadi
    except WebSocketDisconnect:
        print("connection closed")
        active_connections.remove(websocket)

@router.get("/assigned-driver-location")
async def get_assigned_driver_location(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    location = await crud.get_driver_location_for_user(db, current_user.id)
    if not location:
        raise HTTPException(status_code=404, detail="Haydovchi yoki joylashuv topilmadi")
    return {
        "driver_id": location.user_id,
        "lat": location.latitude,
        "lng": location.longitude,
        "timestamp": location.timestamp
    }
