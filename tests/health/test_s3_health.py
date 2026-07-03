
import os,socket,pytest
pytestmark=pytest.mark.health
def test_s3_tcp_is_open():
    host=os.getenv("QA_S3_HOST");port=int(os.getenv("QA_S3_PORT","9000"))
    if not host: pytest.skip("QA_S3_HOST is not configured")
    with socket.create_connection((host,port),timeout=5): pass
