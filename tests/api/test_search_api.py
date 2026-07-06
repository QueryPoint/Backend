
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import uuid4
from src.api.search.router import router
from src.api.search.dependencies import get_search_service
from src.api.auth.dependencies import get_current_user_id


def client_with(service):
    app=FastAPI();app.include_router(router)
    app.dependency_overrides[get_search_service]=lambda:service
    app.dependency_overrides[get_current_user_id]=lambda:uuid4()
    return TestClient(app)

def test_search_requires_query_parameter():
    class Service: pass
    assert client_with(Service()).get('/api/v1/search').status_code==422

def test_search_rejects_empty_query():
    class Service: pass
    assert client_with(Service()).get('/api/v1/search?q=').status_code==422

def test_search_passes_limit_and_offset_to_service():
    received = {}
    class Service:
        async def search(self, user_id, q, limit, offset):
            received['limit'] = limit
            received['offset'] = offset
            return []
    client_with(Service()).get('/api/v1/search?q=sql&limit=5&offset=10')
    assert received == {'limit': 5, 'offset': 10}

def test_search_defaults_limit_to_ten():
    received = {}
    class Service:
        async def search(self, user_id, q, limit, offset):
            received['limit'] = limit
            received['offset'] = offset
            return []
    client_with(Service()).get('/api/v1/search?q=sql')
    assert received == {'limit': 10, 'offset': 0}

def test_search_returns_results_in_contract_shape():
    class Service:
        async def search(self,*a): return [{'file_name':'lecture.pdf','page_number':1,'chunk_id':'chunk','text':'found','score':1.0}]
    response=client_with(Service()).get('/api/v1/search?q=sql')
    assert response.status_code==200
    assert response.json()[0]['file_name']=='lecture.pdf'

def test_clear_history_returns_expected_status():
    class Service:
        async def delete(self,*a): return None
    response=client_with(Service()).delete('/api/v1/history')
    assert response.status_code==200 and response.json()=={'status':'history_cleared'}
