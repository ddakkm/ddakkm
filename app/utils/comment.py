from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.models.comments import Comment as CommentModel
from app.db.session import SessionLocal
from app.schemas import Comment as CommentDto
from app.schemas import NestedComment


def comment_model_to_dto(comment_models: List[CommentModel]) -> List[CommentDto]:
    # Nested Comment / Comment 분리
    comment_dto = [
        CommentDto(
            id=comment.id,
            user_id=comment.user_id,
            nickname=comment.user.nickname,
            content=comment.content,
            created_at=comment.created_at,
            is_delete=comment.is_delete,
            like_count=comment.like_count,
            nested_comment=[NestedComment(
                id=nested_comment.id,
                user_id=nested_comment.user_id,
                nickname=nested_comment.user.nickname,
                content=nested_comment.content,
                created_at=nested_comment.created_at,
                is_delete=nested_comment.is_delete,
                like_count=nested_comment.like_count)
                for nested_comment in comment_models if nested_comment.parent_id == comment.id])
        for comment in comment_models if comment.parent_id is None
    ]
    for comment in comment_dto:
        if comment.is_delete is True:
            comment.nickname = "삭제됨"
            comment.content = "삭제됨"
        for nested in comment.nested_comment:
            if nested.is_delete is True:
                nested.nickname = "삭제됨"
                nested.content = "삭제됨"

    return comment_dto


if __name__ == "__main__":
    comment_models = crud.review.get_review_details(db=SessionLocal(), review_id=3).comments
    ex = comment_model_to_dto(comment_models)
    print(ex)