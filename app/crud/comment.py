from typing import List

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app import crud, models
from app.crud.base import CRUDBase
from app.models.users import User
from app.models.comments import Comment
from app.utils.review import check_is_deleted
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def get_comments_by_review_id(self, db: Session, review_id) -> List[Comment]:
        comment_obj = db.query(self.model).outerjoin(self.model.user).\
            options(joinedload(self.model.user)).filter(self.model.review_id == review_id).all()
        return comment_obj

    def get_comment(self, db: Session, id: int) -> Comment:
        comment_obj = db.query(self.model).filter(self.model.id == id).first()
        if comment_obj is None:
            raise HTTPException(404, "댓글을 찾을 수 없습니다.")
        return comment_obj

    def edit_comment(self, db: Session, id: int, obj_in: CommentUpdate, user_id: int) -> Comment:
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj is None or db_obj.user_id != user_id or db_obj.is_delete is True:
            raise HTTPException(401, "수정 권한이 없는 댓글입니다.")
        db_obj.content = obj_in.content
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_by_current_user(self, db: Session, *, obj_in: CommentCreate, current_user: User, review_id: int) -> Comment:
        db_obj = self.model(
            user_id=current_user.id,
            review_id=review_id,
            content=obj_in.content
        )
        review = crud.review.get_review(db=db, id=review_id)
        check_is_deleted(review)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_nested_comment(self, db: Session, *,
                              obj_in: CommentCreate, current_user: User, comment_id: int) -> Comment:
        comment_obj = self.get_comment(db, id=comment_id)
        if comment_obj.depth == 1:
            raise HTTPException(400, "대댓글에는 대댓글을 달 수 없습니다.")
        if comment_obj.is_delete is True:
            raise HTTPException(400, "이미 삭제된 댓글입니다.")
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

    def get_review_id_by_comment_user_id(self, db: Session, user_id: int):
        result = db.query(self.model.review_id).\
            filter(self.model.user_id == user_id).group_by(self.model.review_id).all()
        return result

    def get_comment_counts_by_user_id(self, db: Session, user_id: int) -> int:
        counts = db.query(self.model).filter(self.model.user_id == user_id).count()
        return counts

    def get_comment_counts_by_review_id(self, db: Session, review_id: int) -> int:
        counts = db.query(self.model).filter(self.model.review_id == review_id).count()
        return counts


comment = CRUDComment(Comment)