from typing import Dict, List

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app import crud, models, schemas
from app.core.config import settings
from app.controllers.deps import get_current_user

database_uri = f"mysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_SERVER}:3306/{settings.MYSQL_DB}?charset=utf8mb4"

engine = create_engine(database_uri, pool_pre_ping=True, pool_size=15, max_overflow=0, encoding='utf8')

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

SAMPLE_JOIN_SURVEY_PARAMS = {
  "survey_type": "A",
  "survey_details": {
    "vaccine_type": "ETC",
    "vaccine_round": "FIRST",
    "is_crossed": False,
    "is_pregnant": False,
    "is_underlying_disease": False,
    "date_from": "ZERO_DAY",
    "data": {
      "q1": [1, 2, 3, 4, 5, 6, 7, "근육통 이요? 근육이 애초에 없었는데요"],
      "q2": [2],
      "q2_1": [2],
      "q3": [1, 2, 3, 4, "두통이요? 저는 머리가 없습니다."],
      "q4": [1, 2, 3, 4, 5, "속이요? 저는 다이어터인데요."],
      "q5": [1]
    }
  }
}


def post_sample_review(client: TestClient, db: Session, host: str, get_test_user_token: Dict[str, str]) -> int:
    body = SAMPLE_REVIEW_PARAMS.copy()
    body["keywords"] = []
    body["content"] = "sample_review_60ZXlSGZ2gtZXoOPNsxsBYttZVbAhvZZ"
    sample_review = client.post(host, json=body, headers=get_test_user_token)
    db.commit()
    db.close()
    assert sample_review.status_code == 200
    sample_review_id = sample_review.json().get("object")
    return sample_review_id


def delete_sample_review(db: Session, review_id: int):
    sample_review = crud.review.get_review(db, id=review_id)
    db.query(models.ReviewKeyword).filter(models.ReviewKeyword.review_id == review_id).delete()
    db.query(models.Comment).filter(models.Comment.review_id == review_id).delete()
    db.delete(sample_review)
    db.delete(sample_review.survey)
    db.commit()
    db.close()


def post_sameple_comment(client: TestClient, host: str, review_id: int, get_test_user_token: Dict[str, str]) -> int:
    comment = {"content": "XQbw54tP7n"}
    post_comment_response = client.post(
        f"{host}/{review_id}/comment", headers=get_test_user_token, json=comment
    )
    assert post_comment_response.status_code == 200
    return post_comment_response.json().get("object")


def post_sample_nested_comment(client: TestClient, host: str, comment_id: int, get_test_user_tokne: Dict[str, str]) -> int:
    comment = {"content": "GOgxXz4Pb0"}
    post_nested_comment_response = client.post(
        f"{host}/{comment_id}", headers=get_test_user_tokne, json=comment
    )
    assert post_nested_comment_response.status_code == 200
    return post_nested_comment_response.json().get("object")


def get_review_ids_has_comment(db: Session):
    reviews = crud.review.get_reviews_has_comment(db)
    return [review.id for review in reviews]


def get_user_model(db: Session, get_test_user_token: Dict[str, str]):
    token = get_test_user_token.get("Authorization")[7:]
    user = get_current_user(db=db, token=token)
    return crud.user.get(db, id=user.id)
