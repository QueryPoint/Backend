
import os,pytest,httpx
pytestmark=pytest.mark.health
def test_elasticsearch_cluster_responds():
    url=os.getenv("QA_ELASTICSEARCH_URL")
    if not url: pytest.skip("QA_ELASTICSEARCH_URL is not configured")
    response=httpx.get(url.rstrip("/")+"/_cluster/health",timeout=5)
    assert response.status_code==200
    assert response.json()["status"] in {"green","yellow"}
