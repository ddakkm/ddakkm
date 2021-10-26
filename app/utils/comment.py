from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.models.comments import Comment as CommentModel
from app.db.session import SessionLocal
from app.schemas import Comment as CommentDto
from app.schemas import NestedComment


def comment_model_to_dto(comment_models: List[CommentModel]) -> List[CommentDto]:
    # TODO O(N^2) 말고 다른 방법 없나
    comment_dtos = [
        CommentDto(
            id=comment.id,
            user_id=comment.user_id,
            nickname=comment.user.nickname,
            content=comment.content,
            created_at=comment.created_at,
            nested_comment=[NestedComment(
                id=nested_comment.id,
                user_id=nested_comment.user_id,
                nickname=nested_comment.user.nickname,
                content=nested_comment.content,
                created_at=nested_comment.created_at
            )
                for nested_comment in comment_models if nested_comment.parent_id == comment.id]
        ) for comment in comment_models if comment.parent_id is None
    ]
    return comment_dtos


if __name__ == "__main__":
    comment_models = crud.review.get_review_details(db=SessionLocal(), review_id=3).comments
    ex = comment_model_to_dto(comment_models)
    print(ex)