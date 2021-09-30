from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.crud.survey import survey_a
from app.models.reviews import Review
from app.schemas.review import ReviewCreateParams, ReviewUpdate, ReviewCreate


class CRUDReview(CRUDBase[Review, ReviewCreateParams, ReviewUpdate]):
    def create(self, db: Session, *, obj_in: ReviewCreateParams):
        survey_create_schema = obj_in.survey
        survey_id = survey_a.create(db=db, obj_in=survey_create_schema).id
        db_obj = Review(
            writer_id=obj_in.writer_id,
            survey_id=survey_id,
            content=obj_in.content,
            images=jsonable_encoder(obj_in.images),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


review = CRUDReview(Review)
