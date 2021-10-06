import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestGetReviews:
    # Only Check Status Code
    def test_get_reviews(self):
        response = client.get("/v1/reviews")
        assert response.status_code == 404
