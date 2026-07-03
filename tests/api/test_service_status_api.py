
from fastapi.testclient import TestClient
from src.main import app

def test_ping_endpoint_is_available_without_lifespan():
    # Не используем контекст TestClient, чтобы не запускать реальные внешние сервисы в lifespan.
    client=TestClient(app, raise_server_exceptions=False)
    response=client.get('/')
    assert response.status_code==200
    assert response.json()=={'ping':'pong'}
