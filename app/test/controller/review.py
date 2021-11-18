import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, crud
from app.main import app
from app.test.utils import TestingSessionLocal
from app.utils.user import calculate_birth_year_from_age

client = TestClient(app)


class TestGetReviews:
    host = "/v1/review"
    db: Session = TestingSessionLocal()

    # Only Check Status Code
    def test_get_reviews(self):
        response = client.get(self.host)
        assert response.status_code == 200

    def test_get_review_with_user_filter(self):
        query_params = "?q=백신" \
                       "&min_age=0&max_age=1000" \
                       "&gender=ETC"
        response = client.get(self.host+query_params).json()
        content = response.get("contents")
        if len(content) > 0:
            user = crud.user.get(db=self.db, id=content[0].get("user_id"))
            assert "백신" in content[0].get("content")
            assert 0 <= calculate_birth_year_from_age(user.age) <= 1000
            assert user.gender == "ETC"
