from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import models
from app.routers import auth, users, location,emergency,drivers,websocket  # Routerlarni shu yerga qo‘shing

app = FastAPI(
    title="Ambulance Real-Time API",
    description="FastAPI asosidagi tez yordam monitoring tizimi",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Agar frontend domeni bo‘lsa, o‘rniga yozing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlarni ulash
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(location.router)
app.include_router(emergency.router)
app.include_router(drivers.router)
app.include_router(websocket.router)


# Startup event orqali jadval yaratish
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

