import os, sys
from typing import Dict, Generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


SAMPLE_REVIEW_PARAMS = {
        "content": " asdasd ",
        "survey": {
            "vaccine_type": "ETC",
            "vaccine_round": "FIRST",
            "is_crossed": False,
            "is_pregnant": False,
            "is_underlying_disease": False,
            "date_from": "ZERO_DAY",
            "data": {
                "q1": [1],
                "q2": [1],
                "q2_1": [],
                "q3": [1],
                "q4": [1],
                "q5": [1]
            }
        },
        "keywords": ["심근염/심낭염"],
        "images": {
            "image1_url": "https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/images/32c6f15b-3c50-59b3-8d3a-e98bfc223517.jpeg",
            "image2_url": None,
            "image3_url": None
        }
    }


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
