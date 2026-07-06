
"""Нагрузка поиска. Запуск: uv run locust -f tests/load/locustfile.py --host http://localhost:8000"""
import os
from locust import HttpUser, task, between

class SearchUser(HttpUser):
    wait_time=between(0.3,1.2)
    def on_start(self):
        self.client.post("/api/v1/login",json={
            "username":os.getenv("QA_LOAD_USERNAME","qa_user"),
            "password":os.getenv("QA_LOAD_PASSWORD","123456"),
        },name="login")
    @task(4)
    def search_existing(self):
        self.client.get("/api/v1/search",params={"q":os.getenv("QA_LOAD_QUERY","базы данных")},name="search existing")
    @task(1)
    def search_empty(self):
        self.client.get("/api/v1/search",params={"q":"qwerty_not_found_qa"},name="search no results")
