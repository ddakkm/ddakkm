from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import crud, schemas
from app.crud.base import CRUDBase
from app.models.users import User
from app.models.user_comment_like import UserCommentLike
from app.schemas.user_comment_like import UserCommentLikeCreate, UserCommentLikeUpdate


class CRUDUserCommentLike(CRUDBase[UserCommentLike, UserCommentLikeCreate, UserCommentLikeUpdate]):
    def change_user_comment_like_status(self, db: Session, current_user: User, comment_id: int) -> schemas.BaseResponse:
        comment = crud.comment.get_comment(db, id=comment_id)
        if not comment:
            raise HTTPException(404, "좋아요 할 댓글을 찾을 수 없습니다.")

        # 이미 좋아요 한 상태면 좋아요 기록 삭제
        check_like = db.query(self.model).\
            filter(self.model.user_id == current_user.id).filter(self.model.comment_id == comment_id).first()
        if check_like:
            db.delete(check_like)
            comment.like_count -= 1
            db.add(comment)
            db.commit()
            db.refresh(comment)
            response = schemas.BaseResponse(
                object=comment_id, message=f"댓글 ID : #{comment_id}에 대해 유저 ID : #{current_user.id}가 좋아요를 취소했습니다."
            )
            return response

        # 좋아요 안한 상태면 좋아요 기록 생성
        else:
            db_obj = self.model(user_id=current_user.id, comment_id=comment_id)
            comment.like_count += 1
            db.add(comment)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            response = schemas.BaseResponse(
                object=comment_id, message=f"댓글 ID : #{comment_id}에 대해 유저 ID : #{current_user.id}가 좋아요하였습니다."
            )
            return response

    def get_comment_id_by_user_id(self, db: Session, user_id: int):
        result = db.query(self.model.comment_id).\
            filter(self.model.user_id == user_id).group_by(self.model.comment_id).all()
        return result


user_comment_like = CRUDUserCommentLike(UserCommentLike)
