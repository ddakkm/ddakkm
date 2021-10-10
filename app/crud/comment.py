from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.base import CRUDBase
from app.models.users import User
from app.models.comments import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def get_comment(self, db: Session, id: int) -> Comment:
        comment_obj = db.query(self.model).filter(self.model.id == id).filter(self.model.is_delete == False).first()
        if comment_obj is None:
            raise HTTPException(404, "댓글을 찾을 수 없습니다.")
        return comment_obj

    def create_by_current_user(self, db: Session, *, obj_in: CommentCreate, current_user: User, review_id) -> Comment:
        db_obj = self.model(
            user_id=current_user.id,
            review_id=review_id,
            content=obj_in.content
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_nested_comment(self, db: Session, *,
                              obj_in: CommentCreate, current_user: User, comment_id: int) -> Comment:
        comment_obj = self.get_comment(db, id=comment_id)
        review_id = comment_obj.review_id

        db_obj = self.model(
            user_id=current_user.id,
            review_id=review_id,
            parent_id=comment_id,
            depth=1,
            content=obj_in.content
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def set_comment_status_as_deleted(db: Session, *, db_obj: Comment, current_user: User) -> Comment:
        if current_user.is_super is True or db_obj.user_id == current_user.id:
            db_obj.is_delete = True
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            raise HTTPException(401, "이 게시글을 수정할 권한이 없습니다.")


comment = CRUDComment(Comment)