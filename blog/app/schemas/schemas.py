from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.models import UserRole
class UserBase(BaseModel):
    username: str
    email: str
    role: str  # "user" yoki "driver"

class UserCreate(UserBase):
    password: str
    phone_number: Optional[str] = None
    
class User(UserBase):
    id: int
    is_active: bool
    phone_number: Optional[str] = None
    class Config:
        orm_mode = True

class UserOut(UserBase):
    id: int
    is_active: bool
    role: UserRole
    hospital_id: Optional[int]
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float

class LocationOut(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        orm_mode = True
        
class RequestStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    accepted = "accepted"
    completed = "completed"
    cancelled = "cancelled"
    
class DriverBase(BaseModel):
    user_id: int
    car_number: str
    car_type: Optional[str] = None
    phone_number: str
    is_available: Optional[bool] = False
    current_latitude: float
    current_longitude: float
    
    hospital_id: int


class DriverCreate(DriverBase):
    pass


class DriverUpdateLocation(BaseModel):
    latitude: float
    longitude: float


class DriverOut(DriverBase):
    id: int

    class Config:
        orm_mode = True
        
#   EMERGENCY REQUEST SCHEMAS

class EmergencyRequestBase(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    description: Optional[str] = None
    hospital_id: int


class EmergencyRequestCreate(EmergencyRequestBase):
    user_id: int  # so‘rov jo‘natuvchi user ID


class EmergencyRequestUpdate(BaseModel):
    driver_id: Optional[int] = None
    status: Optional[RequestStatus] = None
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class EmergencyRequestOut(EmergencyRequestBase):
    id: int
    user_id: int
    driver_id: Optional[int] = None
    status: RequestStatus
    created_at: datetime
    assigned_at: Optional[datetime]
    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True

#hospital
class HospitalBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    phone_number: Optional[str] = None

class HospitalCreate(HospitalBase):
    pass

class HospitalResponse(HospitalBase):
    id: int
    class Config:
        orm_mode = True
        
# DriverCreate	Haydovchi yaratishda ishlatiladi
# DriverOut	Frontendga haydovchi ma’lumotini yuborish
# DriverUpdateLocation	Lokatsiyani real-time yangilash uchun
# EmergencyRequestCreate	Yangi favqulodda so‘rov yaratish
# EmergencyRequestUpdate	So‘rovni yangilash: status, haydovchi biriktirish, vaqtlar
# EmergencyRequestOut	Frontendga yuboriladigan to‘liq javob
# RequestStatus	Statuslar enum ko‘rinishida: pending, assigned, h.k.