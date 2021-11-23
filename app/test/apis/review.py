import os, sys
from typing import Dict
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.main import app
from app.test.utils import TestingSessionLocal
from app.utils.user import calculate_birth_year_from_age

client = TestClient(app)


class TestGetReviews:
    host = "/v1/review"
    db: Session = TestingSessionLocal()

    def test_get_reviews(self):
        response = client.get(self.host)
        assert response.status_code == 200

    def test_get_review_with_user_filter(self):
        query_params = "?q=백신" \
                       "&min_age=30&max_age=39" \
                       "&gender=FEMALE"
        response = client.get(self.host+query_params).json()
        content = response.get("contents")
        if len(content) > 0:
            user = crud.user.get(db=self.db, id=content[0].get("user_id"))
            assert "백신" in content[0].get("content")
            assert 30 <= calculate_birth_year_from_age(user.age) <= 39
            assert user.gender == "FEMALE"

    def test_get_review_with_vaccine_filter(self):
        query_params = "?vaccine_type=MODERNA" \
                       "&is_crossed=false" \
                       "&round=FIRST" \
                       "&is_pregnant=false" \
                       "&is_underlying_disease=false"
        response = client.get(self.host+query_params).json()
        content = response.get("contents")
        if len(content) > 0:
            for review in content:
                review_model = crud.review.get_review(db=self.db, id=review.get("id"))
                assert review.get("vaccine_type") == "MODERNA"
                assert review.get("vaccine_round") == "FIRST"
                assert review_model.survey.is_pregnant == False
                assert review_model.survey.is_underlying_disease == False

    def test_pagenation(self):
        page = 1
        total = 0
        contents_count = 0
        has_next = True
        while has_next:
            query_params = f"?page={page}"
            response = client.get(self.host+query_params).json()
            page_meta = response.get("page_meta")

            total = page_meta.get("total")
            contents_count += len(response.get("contents"))

            has_next = page_meta.get("has_next")
            page += 1

        assert total == contents_count


class TestPostReview:
    host = "v1/review"
    db: Session = TestingSessionLocal()
    default_params = {
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
            "image2_url": "string",
            "image3_url": "string"
        }
    }

    def test_post_review(self, get_test_user_token: Dict[str, str]):
        response = client.post(self.host, json=self.default_params, headers=get_test_user_token)
        review_id = response.json().get("object")
        test_review = crud.review.get_review(self.db, id=review_id)
        self.db.delete(test_review)
        self.db.commit()
        self.db.close()
        assert response.status_code == 200

    def test_without_content_not_accept(self, get_test_user_token: Dict[str, str]):
        body = self.default_params.copy()
        response = client.post(self.host, json=body.pop("content"), headers=get_test_user_token)
        assert response.status_code != 200

    def test_without_keyword_accept(self, get_test_user_token: Dict[str, str]):
        body = self.default_params.copy()
        body["keywords"] = []
        response = client.post(self.host, json=body, headers=get_test_user_token)
        review_id = response.json().get("object")
        test_review = crud.review.get_review(self.db, id=review_id)
        self.db.delete(test_review)
        self.db.commit()
        self.db.close()
        assert response.status_code == 200


class TestPostImages:
    host = "v1/review/images"
    db: Session = TestingSessionLocal()

    def test_post_images(self, get_test_user_token: Dict[str, str]):
        file1 = open("docs/test_images/test1.jpeg", "rb")
        file2 = open("docs/test_images/test2.jpeg", "rb")
        file3 = open("docs/test_images/test3.jpg", "rb")
        files = [('files', file1), ('files', file2), ('files', file3)]
        response = client.post(self.host, files=files, headers=get_test_user_token)
        file1.close()
        file2.close()
        file3.close()
        assert dict(response.json()) == {
            'image1_url': 'https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/'
                          'images/21726e00-63cd-5750-b186-c786400a649e.jpeg',
            'image2_url': 'https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/'
                          'images/f413c8d2-9320-5e45-bdfb-55d89b1e194d.jpeg',
            'image3_url': 'https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/'
                          'images/017a8e3c-a6f1-5e06-ada9-4bb49485f4cd.jpg'
        }

    def test_post_image(self, get_test_user_token: Dict[str, str]):
        file1 = open("docs/test_images/test1.jpeg", "rb")
        files = [('files', file1)]
        response = client.post(self.host, files=files, headers=get_test_user_token)
        file1.close()
        print(response.json())
        assert dict(response.json()) == {
            'image1_url': 'https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/'
                          'images/21726e00-63cd-5750-b186-c786400a649e.jpeg',
            'image2_url': None,
            'image3_url': None
        }

