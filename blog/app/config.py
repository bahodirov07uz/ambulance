from passlib.context import CryptContext
from pydantic_settings import BaseSettings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
