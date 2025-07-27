from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import Driver, EmergencyRequest, RequestStatus,Hospital
from ..schemas.schemas import DriverCreate, EmergencyRequestCreate
from datetime import datetime
from math import sqrt


# Haydovchini eng yaqiniga biriktirib request yaratish
async def create_emergency_request(db: AsyncSession, data: EmergencyRequestCreate):
    # 1. Eng yaqin hospitalni topamiz
    result = await db.execute(select(Hospital))
    hospitals = result.scalars().all()

    if not hospitals:
        raise Exception("Hech qanday hospital mavjud emas")

    def hospital_distance(hosp):
        return sqrt(
            (hosp.latitude - data.latitude) ** 2 +
            (hosp.longitude - data.longitude) ** 2
        )

    nearest_hospital = min(hospitals, key=hospital_distance)

    # 2. Requestni yaratamiz, hospital_id bilan
    request = EmergencyRequest(
        **data.dict(),
        status=RequestStatus.PENDING,
        hospital_id=nearest_hospital.id
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)

    # 3. Shu hospitaldagi available haydovchilarni topamiz
    driver_result = await db.execute(
        select(Driver).where(
            Driver.is_available == True,
            Driver.hospital_id == nearest_hospital.id
        )
    )
    drivers = driver_result.scalars().all()

    if not drivers:
        return request  # Hozircha available driver yo‘q

    def calc_distance(driver):
        return sqrt(
            (driver.current_latitude - data.latitude) ** 2 +
            (driver.current_longitude - data.longitude) ** 2
        )

    nearest_driver = min(drivers, key=calc_distance)

    # 4. Driverni requestga biriktiramiz
    request.driver_id = nearest_driver.user_id
    request.status = RequestStatus.ASSIGNED
    request.assigned_at = datetime.utcnow()
    nearest_driver.is_available = False

    await db.commit()
    await db.refresh(request)
    return request

# Haydovchini so‘rovga qo‘lda biriktirish (fallback yoki admin uchun)
async def assign_driver(db: AsyncSession, request_id: int, driver_id: int):
    result = await db.execute(select(EmergencyRequest).where(EmergencyRequest.id == request_id))
    req = result.scalar_one_or_none()

    if req:
        req.driver_id = driver_id
        req.status = RequestStatus.ASSIGNED
        req.assigned_at = datetime.utcnow()

        # Haydovchini band qilish
        driver_result = await db.execute(select(Driver).where(Driver.id == driver_id))
        driver = driver_result.scalar_one_or_none()
        if driver:
            driver.is_available = False

        await db.commit()
        await db.refresh(req)
        return req
    return {
        "status": "assigned",
        "driver_id": driver.user_id,
        "request_id": req.id,
        "assigned_at": req.assigned_at.isoformat()
    }

# Haydovchining real-time lokatsiyasini yangilash
async def update_driver_location(db: AsyncSession, driver_id: int, lat: float, lng: float):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if driver:
        driver.current_latitude = lat
        driver.current_longitude = lng
        await db.commit()
        await db.refresh(driver)
        return driver
    return {
        "status": "success",
        "driver_id": driver.user_id,
        "new_latitude": driver.current_latitude,
        "new_longitude": driver.current_longitude,
    }