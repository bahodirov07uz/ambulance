from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # optional: listen client messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)
