from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.models.comments import Comment as CommentModel
from app.db.session import SessionLocal
from app.schemas import Comment as CommentDto
from app.schemas import NestedComment


def comment_model_to_dto(
        comment_models: List[CommentModel], comment_ids_like_by_user: List[int], current_user_id: int
) -> List[CommentDto]:

    for comment in comment_models:
        if comment.is_delete is True:
            comment.content = "삭제된 댓글입니다."
        if comment.user.is_active is False:
            comment.nickname = "탈퇴한 회원"
            comment.content = "탈퇴한 작성자의 댓글입니다."

    comment_dto = [
        CommentDto(
            id=comment.id,
            user_id=comment.user_id,
            nickname=comment.user.nickname,
            content=comment.content,
            created_at=comment.created_at,
            like_count=comment.like_count,
            user_is_like=comment.id in comment_ids_like_by_user,
            user_is_writer=comment.user.id == current_user_id,
            nested_comment=[NestedComment(
                id=nested_comment.id,
                user_id=nested_comment.user_id,
                nickname=nested_comment.user.nickname,
                content=nested_comment.content,
                created_at=nested_comment.created_at,
                like_count=nested_comment.like_count,
                user_is_like=nested_comment.id in comment_ids_like_by_user,
                user_is_writer=nested_comment.user.id == current_user_id,
            )
                for nested_comment in comment_models if nested_comment.parent_id == comment.id])
        for comment in comment_models if comment.parent_id is None
    ]

    return comment_dto
