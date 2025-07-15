from fastapi import FastAPI, Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, List
from urllib.parse import parse_qs
from fastapi.middleware.cors import CORSMiddleware

from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # yoki frontend manzilingiz masalan: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# WebSocket connections
active_connections: List[WebSocket] = []

# === Dependencies ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# === Routes ===

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/drivers/", response_model=List[schemas.UserOut])
def read_drivers(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.get_users_by_role(db, role="driver", skip=skip, limit=limit)

@app.post("/update_location")
async def update_location(location: schemas.LocationUpdate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    crud.update_user_location(db, current_user.id, location)
    
    for connection in active_connections:
        await connection.send_json({
            "user_id": current_user.id,
            "lat": location.latitude,
            "lng": location.longitude
        })
    
    return {"status": "Location updated"}


@app.websocket("/ws/location")
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
            await websocket.receive_text()  # ❗ bu yer kerak!
    except:
        print("connection closed")
        active_connections.remove(websocket)

@app.get("/assigned-driver-location")
def get_assigned_driver_location(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    location = crud.get_driver_location_for_user(db, current_user.id)
    if not location:
        raise HTTPException(status_code=404, detail="Driver or location not found")
    return {
        "driver_id": location.user_id,
        "lat": location.latitude,
        "lng": location.longitude,
        "timestamp": location.timestamp
    }
