
import os,socket,pytest
pytestmark=pytest.mark.health
def test_rabbitmq_tcp_is_open():
    host=os.getenv("QA_RABBITMQ_HOST");port=int(os.getenv("QA_RABBITMQ_PORT","5672"))
    if not host: pytest.skip("QA_RABBITMQ_HOST is not configured")
    with socket.create_connection((host,port),timeout=5): pass
