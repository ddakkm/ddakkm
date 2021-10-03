from typing import List

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.crud.survey import survey_a
from app.models.reviews import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def create(self, db: Session, *, obj_in: ReviewCreate):
        print(obj_in)
        survey_create_schema = obj_in.survey
        survey_id = survey_a.create(db=db, obj_in=survey_create_schema).id
        db_obj = Review(
            user_id=obj_in.user_id,
            survey_id=survey_id,
            content=obj_in.content,
            images=jsonable_encoder(obj_in.images),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        return db.query(self.model).offset(skip).limit(limit).all()


review = CRUDReview(Review)
