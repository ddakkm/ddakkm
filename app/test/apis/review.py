import copy
import os, sys
from typing import Dict

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
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

    def test_get_review_list_model(self):
        response = client.get(self.host)
        response_body = response.json()
        if len(response_body.get("contents")) > 0:
            example_content = response_body.get("contents")[0]
            schemas.ReviewResponse(
                id=example_content.get("id"),
                user_id=example_content.get("user_id"),
                nickname=example_content.get("nickname"),
                vaccine_round=example_content.get("vaccine_round"),
                vaccine_type=example_content.get("vaccine_type"),
                is_crossed=example_content.get("is_crossed"),
                symptom=example_content.get("symptom"),
                content=example_content.get("content"),
                like_count=example_content.get("like_count"),
                comment_count=example_content.get("comment_count"),
                user_is_like=example_content.get("user_is_like")
            )


class TestReivewBase:
    host = "v1/review"
    db: Session = TestingSessionLocal()
    reviews = crud.review.get_multi(db=db)
    abnormal_review_ids = []
    normal_review_ids = []

    def test_get_review_status_ok(self):
        for review in self.reviews:
            if review.is_delete is True or review.user.is_active is False:
                self.abnormal_review_ids.append(review.id)
            else:
                self.normal_review_ids.append(review.id)

        for review_id in self.normal_review_ids:
            response = client.get(self.host+"/"+str(review_id))
            assert response.status_code == 200

        for review_id in self.abnormal_review_ids:
            response = client.get(self.host+"/"+str(review_id))
            assert response.status_code == 404

    # 리뷰 모델에 맞게 리턴되는지 확인
    def test_get_review_model(self):
        response = client.get(self.host+"/"+str(self.normal_review_ids[0]))
        response_body = response.json()
        schemas.Review(
            id=response_body.get("id"),
            survey=response_body.get("survey"),
            user_id=response_body.get("user_id"),
            user_gender=response_body.get("user_gender"),
            user_age_group=response_body.get("user_age_group"),
            content=response_body.get("content"),
            is_writer=response_body.get("is_writer"),
            nickname=response_body.get("nickname"),
            keyword=response_body.get("keywords"),
            comment_count=response_body.get("comment_count"),
            like_count=response_body.get("like_count"),
            images=response_body.get("images", None),
            user_is_like=response_body.get("user_is_like")
        )

    def test_get_review_content(self, get_test_user_token: Dict[str, str]):
        response = client.get(f"{self.host}/{self.normal_review_ids[0]}/content", headers=get_test_user_token)
        assert response.status_code == 200
