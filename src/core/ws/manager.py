from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    def add(self, connection_id: str, websocket: WebSocket) -> None:
        self._connections[connection_id] = websocket

    def remove(self, connection_id: str) -> None:
        self._connections.pop(connection_id, None)

    async def send(self, connection_id: str, data: dict) -> bool:
        websocket = self._connections.get(connection_id)
        if websocket is None:
            return False
        await websocket.send_json(data)
        return True


connection_manager = ConnectionManager()