# app/init_db.py deb alohida fayl oching:

from app.models import models
from app.database import engine

async def recreate_db():
    async with engine.begin() as conn:
        print("Dropping and recreating tables...")
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
