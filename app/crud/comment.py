from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.users import User
from app.models.comments import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDSurveyA(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def create_by_current_user(self, db: Session, *, obj_in: CommentCreate, current_user: User, review_id):
        db_obj = self.model(
            user_id=current_user.id,
            review_id=review_id,
            content=obj_in.content
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


comment = CRUDSurveyA(Comment)