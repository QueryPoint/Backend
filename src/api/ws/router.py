from uuid import UUID, uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.api.auth.security import decode_token
from src.core.ws.manager import connection_manager
from src.core.ws.state import (
    set_connection,
    delete_connection,
    set_status,
    get_status,
    delete_status,
)
from src.core.ws.enums import WSStatus
from src.core.rabbitmq.to_llm import publish_prompt, publish_delete

router = APIRouter(prefix="/api/v1", tags=["web_socket"])

def _get_user_id(websocket: WebSocket) -> UUID | None:
    access_token = websocket.cookies.get("access_token")
    if not access_token:
        return None

    payload = decode_token(access_token)
    if not payload or payload.get("type") != "access":
        return None
    return UUID(payload["sub"])

async def _handle_prompt(websocket: WebSocket, user_id: UUID, message: dict) -> None:
    status = await get_status(user_id)

    if status == WSStatus.processing.value:
        await websocket.send_json({"type": "error", "data": "Prompt already processing"})
        return

    if status == WSStatus.blocked.value:
        await websocket.send_json({"type": "error", "data": "Chat blocked, reset required"})
        return

    await set_status(user_id, WSStatus.processing)

    await publish_prompt(
        user_id=user_id,
        prompt=message["prompt"],
        doc=message.get("doc"),
    )

async def _handle_delete(user_id: UUID) -> None:
    await publish_delete(user_id)
    await set_status(user_id, WSStatus.idle)

@router.websocket("/ws")
async def ws(websocket: WebSocket):
    user_id = _get_user_id(websocket)
    if user_id is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connection_id = str(uuid4())
    connection_manager.add(connection_id, websocket)
    await set_connection(user_id, connection_id)
    await set_status(user_id, WSStatus.idle)

    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "prompt":
                await _handle_prompt(websocket, user_id, message)
            elif message_type == "delete":
                await _handle_delete(user_id)

    except WebSocketDisconnect:
        connection_manager.remove(connection_id)
        await delete_connection(user_id)
        await delete_status(user_id)
        await publish_delete(user_id)