from typing import List

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.crud.survey import survey_a
from app.models.reviews import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.schemas.survey import SurveyA
from app.schemas.page_response import paginated_query


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def create(self, db: Session, *, obj_in: ReviewCreate):
        # 리뷰 작성을 위한 요청 바디에 포함되어있는 user_id로 서베이를 등록한다.
        survey_create_schema = SurveyA(**jsonable_encoder(obj_in.survey), user_id=obj_in.user_id)
        survey_id = survey_a.create(db=db, obj_in=survey_create_schema).id

        # 서베이 등록 후 리뷰 등록
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

    def get_list_paginated(self, db: Session, page_request: dict) -> List[Review]:
        query = db.query(self.model)

        page = page_request.get("page", 1)
        size = page_request.get("size", 10)

        return paginated_query(
            page_request,
            query,
            lambda x: x.order_by(self.model.id.desc()).limit(size).offset((page - 1) * size).all()
        )


review = CRUDReview(Review)
