
from types import SimpleNamespace
from uuid import uuid4
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.documents.router import router
from src.api.documents.dependencies import get_document_service
from src.api.auth.dependencies import get_current_user_id
from src.api.exc.documents import DocumentNotFound, DocumentForbidden

USER=uuid4()
def client_with(service, user=USER):
    app=FastAPI(); app.include_router(router)
    app.dependency_overrides[get_document_service]=lambda:service
    app.dependency_overrides[get_current_user_id]=lambda:user
    return TestClient(app)

def test_upload_endpoint_returns_uploaded_document_id():
    class Service:
        async def upload(self,user,file): return SimpleNamespace(doc_id=uuid4())
    response=client_with(Service()).post('/api/v1/documents/upload',files={'file':('lecture.pdf',b'%PDF-1.4','application/pdf')})
    assert response.status_code==201 and response.json()['status']=='uploaded'

def test_upload_requires_file_field():
    class Service: pass
    assert client_with(Service()).post('/api/v1/documents/upload').status_code==422

def test_list_validates_limit_and_offset():
    class Service:
        async def list(self,*a): return []
    client=client_with(Service())
    assert client.get('/api/v1/documents?limit=0').status_code==422
    assert client.get('/api/v1/documents?offset=-1').status_code==422
    assert client.get('/api/v1/documents').status_code==200

def test_get_document_not_found_and_forbidden_are_visible():
    class NotFound:
        async def get_one(self,*a): raise DocumentNotFound()
    class Forbidden:
        async def get_one(self,*a): raise DocumentForbidden()
    doc_id=uuid4()
    assert client_with(NotFound()).get(f'/api/v1/documents/{doc_id}').status_code==404
    assert client_with(Forbidden()).get(f'/api/v1/documents/{doc_id}').status_code==403

def test_delete_returns_204():
    class Service:
        async def delete(self,*a): return None
    assert client_with(Service()).delete(f'/api/v1/documents/{uuid4()}').status_code==204
