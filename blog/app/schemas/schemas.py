from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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