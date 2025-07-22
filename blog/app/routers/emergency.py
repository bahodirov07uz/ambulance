from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.schemas import EmergencyRequestCreate, DriverUpdateLocation
from app.dependecies import get_async_session
from ..services import emergency_request as emergency
from ..models.models import EmergencyRequest,Driver
from app.websocket.manager import manager
from sqlalchemy.future import select

router = APIRouter(prefix="/emergency", tags=["Emergency Requests"])


@router.post("/", response_model=EmergencyRequestCreate)
async def create_emergency(
    data: EmergencyRequestCreate,
    db: AsyncSession = Depends(get_async_session)
):
    req = await emergency.create_emergency_request(db, data)
    if not req.driver_id:
        raise HTTPException(status_code=202, detail="Request created, but no driver assigned.")
    
    # 🎯 WebSocket xabari
    await manager.broadcast({
        "event": "new_request",
        "user_id": req.user_id,
        "driver_id": req.driver_id,
        "location": {
            "latitude": req.latitude,
            "longitude": req.longitude
        }
    })

    return req


@router.patch("/driver/{driver_id}/location")
async def update_driver_location(
    driver_id: int,
    data: DriverUpdateLocation,
    db: AsyncSession = Depends(get_async_session)
):
    updated = await emergency.update_driver_location(db, driver_id, data.latitude, data.longitude)
    if not updated:
        raise HTTPException(status_code=404, detail="Driver not found")

    # 🎯 WebSocket xabari
    await manager.broadcast({
        "event": "driver_location_update",
        "driver_id": driver_id,
        "latitude": data.latitude,
        "longitude": data.longitude
    })

    return {"message": "Location updated", "driver_id": driver_id}

@router.post("/emergencies/{emergency_id}/complete")
async def complete_emergency(emergency_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(EmergencyRequest).where(EmergencyRequest.id == emergency_id))
    emergency = result.scalar_one_or_none()

    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency topilmadi")

    # Emergency holatini yakunlangan deb belgilash
    emergency.status = "completed"

    # Unga biriktirilgan driverni bo‘shatamiz
    if emergency.driver_id:
        driver_result = await db.execute(select(Driver).where(Driver.id == emergency.driver_id))
        driver = driver_result.scalar_one_or_none()
        if driver:
            driver.is_available = True

    await db.commit()
    return {"detail": "Emergency yakunlandi va driver bo‘shatildi"}
