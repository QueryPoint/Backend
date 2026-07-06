
import os,socket,pytest
pytestmark=pytest.mark.health
def test_postgres_tcp_is_open():
    host=os.getenv("QA_POSTGRES_HOST");port=int(os.getenv("QA_POSTGRES_PORT","5432"))
    if not host: pytest.skip("QA_POSTGRES_HOST is not configured")
    with socket.create_connection((host,port),timeout=5): pass
