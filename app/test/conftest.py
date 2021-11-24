import os, sys
from typing import Dict, Generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app





@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def get_test_user_token(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.TEST_USER_ID,
        "password": settings.TEST_USER_PW
    }
    r = client.post(f"http://127.0.0.1:8000/v1/auth/login/local", data=login_data)
    response = r.json()
    a_token = response.get("access_token")
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
