import copy
import os, sys
from typing import Dict

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.main import app
from app.test.utils import TestingSessionLocal
from app.utils.user import calculate_birth_year_from_age
from app.test.conftest import SAMPLE_REVIEW_PARAMS

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

    def test_post_review(self, get_test_user_token: Dict[str, str]):
        response = client.post(self.host, json=SAMPLE_REVIEW_PARAMS, headers=get_test_user_token)
        review_id = response.json().get("object")
        test_review = crud.review.get_review(self.db, id=review_id)
        self.db.delete(test_review)
        self.db.query(models.ReviewKeyword).filter(models.ReviewKeyword.review_id == review_id).delete()
        self.db.delete(test_review.survey)
        self.db.commit()
        self.db.close()
        assert response.status_code == 200

    def test_without_content_not_accept(self, get_test_user_token: Dict[str, str]):
        body = SAMPLE_REVIEW_PARAMS.copy()
        response = client.post(self.host, json=body.pop("content"), headers=get_test_user_token)
        assert response.status_code != 200

    def test_without_keyword_accept(self, get_test_user_token: Dict[str, str]):
        body = SAMPLE_REVIEW_PARAMS.copy()
        body["keywords"] = []
        response = client.post(self.host, json=body, headers=get_test_user_token)
        review_id = response.json().get("object")
        test_review = crud.review.get_review(self.db, id=review_id)
        self.db.delete(test_review)
        self.db.query(models.ReviewKeyword).filter(models.ReviewKeyword.review_id == review_id).delete()
        self.db.delete(test_review.survey)
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
        assert dict(response.json()) == {
            'image1_url': 'https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/'
                          'images/21726e00-63cd-5750-b186-c786400a649e.jpeg',
            'image2_url': None,
            'image3_url': None
        }


class TestGetReivew:
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
    def test_get_review_form(self):
        response = client.get(self.host+"/"+str(self.normal_review_ids[0]))
        response_body = response.json()
        schemas.Review(
            id=response_body.get("id"),
            survey=response_body.get("survey"),
            user_id=response_body.get("user_id"),
            content=response_body.get("content"),
            is_writer=response_body.get("is_writer"),
            nickname=response_body.get("nickname"),
            keyword=response_body.get("keywords"),
            comment_count=response_body.get("comment_count"),
            like_count=response_body.get("like_count"),
            images=response_body.get("images", None),
            user_is_like=response_body.get("user_is_like")
        )

    def test_user_is_like(self, get_test_user_token: Dict[str, str]):
        client.post(self.host+"/"+str(self.normal_review_ids[0])+"/like_status", headers=get_test_user_token)
        user_is_like = client.get(self.host+"/"+str(self.normal_review_ids[0]), headers=get_test_user_token).json().get("user_is_like")

        client.post(self.host+"/"+str(self.normal_review_ids[0])+"/like_status", headers=get_test_user_token)
        user_is_unlike = client.get(self.host+"/"+str(self.normal_review_ids[0]), headers=get_test_user_token).json().get("user_is_like")

        assert user_is_like != user_is_unlike
