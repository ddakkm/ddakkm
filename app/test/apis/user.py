import os, sys
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.main import app
from app.test.utils import TestingSessionLocal, get_user_model

client = TestClient(app)


# 회원가입 설문 여부
class TestUserProfile:
    host = "/v1/user"
    db: Session = TestingSessionLocal()

    def test_user_join_survey(self, get_test_user_token: Dict[str, str]):
        user_model = get_user_model(db=self.db, get_test_user_token=get_test_user_token)
        user_response = client.get(f"{self.host}/join-survey", headers=get_test_user_token)
        result = user_response.json().get("done_survey")
        if user_model.join_survey_code:
            join_survey = True
        else:
            join_survey = False
        assert join_survey == result
