import os, sys
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.main import app
from app.test.utils import TestingSessionLocal
from app.test.utils import (
    post_sample_review, delete_sample_review, get_review_ids_has_comment,
    post_sameple_comment, post_sample_nested_comment
)


client = TestClient(app)


class TestCommentBase:
    review_host = "v1/review"
    comment_host = "v1/comment"
    db: Session = TestingSessionLocal()

    def test_post_comment(self, get_test_user_token: Dict[str, str]):
        sample_review_id = post_sample_review(
            client=client, db=self.db, host=self.review_host, get_test_user_token=get_test_user_token
        )
        # 댓글 작성 테스트
        # 댓글을 작성한다.
        post_sameple_comment(
            client=client, host=self.review_host, review_id=sample_review_id, get_test_user_token=get_test_user_token
        )
        # 댓글이 잘 작성되었는지 확인하기 위해 댓글을 단 리뷰 ID로 검색한다.
        posted_review = crud.review.get_review(db=self.db, id=sample_review_id)
        # 리뷰에 처음으로 달린 댓글아이디를 확인한다.
        comment_id = posted_review.comments[0].id
        # 댓글 ID를 통해 검색한다.
        comment_model = crud.comment.get_comment(db=self.db, id=comment_id)
        assert comment_model.review_id == sample_review_id                  # 댓글이 제데로 된 리뷰 아이디에 달렸는지 확인

        # 댓글 내용 가져오기 테스트
        posted_comment = client.get(f"{self.comment_host}/{comment_id}/content", headers=get_test_user_token)
        assert posted_comment.json().get("content") == "XQbw54tP7n"

        # 대댓글 작성 테스트
        post_sample_nested_comment(
            client=client, host=self.comment_host, comment_id=comment_id, get_test_user_tokne=get_test_user_token
        )
        # 댓글 좋아요 테스트
        like_response = client.post(f"{self.comment_host}/{comment_id}/like_status", headers=get_test_user_token)
        assert like_response.status_code == 200

        # 생성된 대댓글을 포함한 댓글 트리
        parent_comment_response = client.get(f"{self.comment_host}/{comment_id}/tree", headers=get_test_user_token)

        # 부모 댓글 id로 자식 댓글 가져오기 테스트
        assert parent_comment_response.status_code == 200
        parent_comment_tree = parent_comment_response.json()
        assert parent_comment_tree.get("user_is_writer") == True                # 작성자 반영 여부 체크
        assert parent_comment_tree.get("user_is_like") == True                  # 좋아요 반영 여부 체크
        dislike_response = client.post(f"{self.comment_host}/{comment_id}/like_status", headers=get_test_user_token)
        assert dislike_response.status_code == 200                              # 좋아요 취소 성공 여부 체크
        sample_nested_comment = parent_comment_tree.get("nested_comment")[0]
        assert sample_nested_comment.get("user_is_writer") == True              # 작성자 반영 여부 체크
        assert sample_nested_comment.get("content") == "GOgxXz4Pb0"             # 작성된 댓글 내용 체크
        delete_sample_review(db=self.db, review_id=sample_review_id)

    def test_report_comment(self, get_test_user_token: Dict[str, str]):
        sample_review_id = post_sample_review(
            client=client, db=self.db, host=self.review_host, get_test_user_token=get_test_user_token
        )
        post_sameple_comment(
            client=client, host=self.review_host, review_id=sample_review_id, get_test_user_token=get_test_user_token
        )
        comment_id = crud.review.get_review(db=self.db, id=sample_review_id).comments[0].id

        response = client.post(
            f"{self.comment_host}/{comment_id}/report", headers=get_test_user_token, json={"reason": 2}
        )
        delete_sample_review(db=self.db, review_id=sample_review_id)
        assert response.status_code == 200

    def test_edit_comment(self, get_test_user_token: Dict[str, str]):
        sample_review_id = post_sample_review(
            client=client, db=self.db, host=self.review_host, get_test_user_token=get_test_user_token
        )
        post_sameple_comment(
            client=client, host=self.review_host, review_id=sample_review_id, get_test_user_token=get_test_user_token
        )
        comment_id = crud.review.get_review(db=self.db, id=sample_review_id).comments[0].id
        client.patch(f"{self.comment_host}/{comment_id}", headers=get_test_user_token, json={"content": "TvbthqLLSw"})
        self.db.commit()
        self.db.close()

        comment_model = crud.comment.get_comment(self.db, id=comment_id)
        assert comment_model.content == "TvbthqLLSw"
        delete_sample_review(db=self.db, review_id=sample_review_id)

    def test_delete_comment(self, get_test_user_token: Dict[str, str]):
        sample_review_id = post_sample_review(
            client=client, db=self.db, host=self.review_host, get_test_user_token=get_test_user_token
        )
        post_sameple_comment(
            client=client, host=self.review_host, review_id=sample_review_id, get_test_user_token=get_test_user_token
        )
        comment_id = crud.review.get_review(db=self.db, id=sample_review_id).comments[0].id
        delete_response = client.delete(f"{self.comment_host}/{comment_id}", headers=get_test_user_token)
        assert delete_response.status_code == 200
        self.db.commit()
        self.db.close()
        get_response = client.get(f"{self.comment_host}/{sample_review_id}")
        posted_comment = get_response.json()[0]
        assert posted_comment.get("content") == "삭제된 댓글입니다."
        delete_sample_review(db=self.db, review_id=sample_review_id)


class TestGetComments:
    host = "v1/comment"
    db: Session = TestingSessionLocal()
    review_ids_has_comment = get_review_ids_has_comment(db)

    def test_get_comments_from_review(self):
        for review_id in self.review_ids_has_comment:
            response = client.get(
                f"{self.host}/{review_id}"
            )
            response_body = response.json()
            assert response.status_code == 200
            for comment in response_body:
                schemas.Comment(
                    id=comment.get("id"),
                    content=comment.get("content"),
                    user_id=comment.get("user_id"),
                    nickname=comment.get("nickname"),
                    like_count=comment.get("like_count"),
                    created_at=comment.get("created_at"),
                    user_is_like=comment.get("user_is_like"),
                    user_is_writer=comment.get("user_is_writer"),
                    nested_comment=comment.get("nested_comment", None)
                )
