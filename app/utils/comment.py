from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.models.comments import Comment as CommentModel
from app.db.session import SessionLocal
from app.schemas import Comment as CommentDto
from app.schemas import NestedComment


def comment_model_to_dto(comment_models: List[CommentModel], comment_ids_like_by_user: List[int]) -> List[CommentDto]:
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
            user_is_like=comment.id in comment_ids_like_by_user,
            user_is_active=comment.user.is_active is True,
            nested_comment=[NestedComment(
                id=nested_comment.id,
                user_id=nested_comment.user_id,
                nickname=nested_comment.user.nickname,
                content=nested_comment.content,
                created_at=nested_comment.created_at,
                is_delete=nested_comment.is_delete,
                like_count=nested_comment.like_count,
                user_is_like=nested_comment.id in comment_ids_like_by_user,
                user_is_active=nested_comment.user.is_active is True
            )
                for nested_comment in comment_models if nested_comment.parent_id == comment.id])
        for comment in comment_models if comment.parent_id is None
    ]
    for comment in comment_dto:
        if comment.is_delete is True:
            comment.content = "삭제된 댓글입니다."
        if comment.user_is_active is False:
            comment.nickname = "탈퇴한 회원"
            comment.content = "탈퇴한 작성자의 댓글입니다."

        for nested in comment.nested_comment:
            if nested.is_delete is True:
                nested.content = "삭제된 댓글입니다."
            if nested.user_is_active is False:
                nested.nickname = "탈퇴한 회원"
                nested.content = "탈퇴한 작성자의 댓글입니다."

    return comment_dto
