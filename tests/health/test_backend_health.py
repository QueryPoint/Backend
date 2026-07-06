
import os, pytest, httpx
pytestmark=pytest.mark.health
def test_backend_ping_is_alive():
    url=os.getenv("QA_BACKEND_URL")
    if not url: pytest.skip("QA_BACKEND_URL is not configured")
    response=httpx.get(url.rstrip("/")+"/",timeout=5)
    assert response.status_code==200
    assert response.json()=={"ping":"pong"}
