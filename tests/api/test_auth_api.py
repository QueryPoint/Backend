
from types import SimpleNamespace
from uuid import uuid4
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.auth.router import router
from src.api.auth.dependencies import get_auth_service
from src.api.exc.auth import Unauthed, UsernameTaken


def app_with(service):
    app=FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_auth_service]=lambda: service
    return TestClient(app)

def test_registration_success_returns_201_and_user():
    class Service:
        async def register(self, username,password): return SimpleNamespace(user_id=uuid4(),username=username)
    client=app_with(Service())
    response=client.post('/api/v1/registration',json={'username':'student_2026','password':'123456'})
    assert response.status_code==201
    assert response.json()['username']=='student_2026'

def test_registration_rejects_boundary_and_invalid_username_before_service():
    class Service:
        async def register(self,*a): raise AssertionError('not called')
    client=app_with(Service())
    for username in ['ab','1student','student-name','студент','a'*26]:
        assert client.post('/api/v1/registration',json={'username':username,'password':'123456'}).status_code==422

def test_registration_returns_400_for_duplicate_username():
    class Service:
        async def register(self,*a): raise UsernameTaken()
    assert app_with(Service()).post('/api/v1/registration',json={'username':'student','password':'123456'}).status_code==400

def test_login_sets_auth_cookies():
    class Service:
        async def login(self,*a): return SimpleNamespace(user_id=uuid4(),username='student',access_token='access',refresh_token='refresh')
    response=app_with(Service()).post('/api/v1/login',json={'username':'student','password':'123456'})
    assert response.status_code==200
    cookies='\n'.join(response.headers.get_list('set-cookie')).lower()
    assert 'access_token=access' in cookies and 'refresh_token=refresh' in cookies and 'httponly' in cookies

def test_refresh_without_cookie_returns_401():
    class Service:
        async def refresh(self, token): raise Unauthed()
    assert app_with(Service()).post('/api/v1/refresh').status_code==401

def test_logout_returns_expected_status():
    class Service:
        async def logout(self,response): return SimpleNamespace(status='logged_out')
    response=app_with(Service()).post('/api/v1/logout')
    assert response.status_code==200 and response.json()=={'status':'logged_out'}
