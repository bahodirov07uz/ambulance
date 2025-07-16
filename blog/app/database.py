from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# sqlite uchun async URL (agar siz PostgreSQL ishlatsangiz, o'zgartirasiz)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# Async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # yoki False, loglarni ko‘rsatadi
    future=True
)

# Async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# ORM Base
Base = declarative_base()
