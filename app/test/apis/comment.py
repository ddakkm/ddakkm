import copy
import os, sys
from typing import Dict

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.main import app
from app.test.utils import TestingSessionLocal
from app.utils.user import calculate_birth_year_from_age
from app.test.utils import SAMPLE_REVIEW_PARAMS, post_sample_review, delete_sample_review

client = TestClient(app)


class TestPostComment:
    host = "v1/review"
    db: Session = TestingSessionLocal()

    def test_post_comment(self, get_test_user_token: Dict[str, str]):
        sample_review_id = post_sample_review(
            client=client, db=self.db, host=self.host, get_test_user_token=get_test_user_token
        )

        comment = {"content": "XQbw54tP7n"}
        post_comment_response = client.post(
            f"{self.host}/{sample_review_id}/comment", headers=get_test_user_token, json=comment
        )
        assert post_comment_response.status_code == 200
        posted_review = crud.review.get_review(db=self.db, id=sample_review_id)
        comment_id = posted_review.comments[0].id

        comment_model = crud.comment.get_comment(db=self.db, id=comment_id)
        assert comment_model.review_id == sample_review_id
        assert comment_model.content == "XQbw54tP7n"
        delete_sample_review(db=self.db, review_id=sample_review_id)
