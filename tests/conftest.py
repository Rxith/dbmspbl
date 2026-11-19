import re

import pytest

from app import create_app

def token_from(response):
    return re.search(rb'name="csrf" value="([^"]+)"', response.data)[1].decode()

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "OPERATOR_PASSWORD": "integration-test"})
    return app.test_client()

@pytest.fixture
def operator(client):
    token = token_from(client.get("/login"))
    response = client.post("/login", data={"csrf": token, "password": "integration-test"})
    assert response.status_code == 302
    return client
