from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    role: str  # "user" yoki "driver"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

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
