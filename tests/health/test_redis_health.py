
import os,socket,pytest
pytestmark=pytest.mark.health
def test_redis_tcp_is_open():
    host=os.getenv("QA_REDIS_HOST");port=int(os.getenv("QA_REDIS_PORT","6379"))
    if not host: pytest.skip("QA_REDIS_HOST is not configured")
    with socket.create_connection((host,port),timeout=5): pass
