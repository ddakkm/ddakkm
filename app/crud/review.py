from typing import List

from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder

from app import models
from app.crud.base import CRUDBase
from app.crud.survey import survey_a
from app.models.reviews import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewParams
from app.schemas.survey import SurveyA
from app.schemas.page_response import paginated_query
from app.utils.user import calculate_birth_year_from_age


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def create_by_current_user(self, db: Session, *, obj_in: ReviewCreate, user_id: int):
        # 리뷰 작성을 위한 요청 바디에 포함되어있는 user_id로 서베이를 등록한다.
        survey_create_schema = SurveyA(**jsonable_encoder(obj_in.survey), user_id=user_id)
        survey_id = survey_a.create(db=db, obj_in=survey_create_schema).id

        # 서베이 등록 후 리뷰 등록
        db_obj = self.model(
            user_id=user_id,
            survey_id=survey_id,
            content=obj_in.content,
            images=jsonable_encoder(obj_in.images),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_list_paginated(self, db: Session, page_request: dict, filters: ReviewParams) -> List[Review]:
        if filters.q:
            filter_query = self.model.content.contains(filters.q)
        else:
            filter_query = self.model.id

        if filters.min_age and filters.max_age:
            min_birth_year = calculate_birth_year_from_age(filters.min_age)
            max_birth_year = calculate_birth_year_from_age(filters.max_age)
            filter_age = models.User.age.between(min_birth_year, max_birth_year)
        else:
            filter_age = self.model.id

        if filters.gender:
            filter_gender = models.User.gender == filters.gender
        else:
            filter_gender = self.model.id

        if filters.vaccine_type:
            filter_vaccine_type = models.SurveyA.vaccine_type == filters.vaccine_type
        else:
            filter_vaccine_type = self.model.id

        if filters.is_crossed is None:
            filter_is_crossed = self.model.id
        elif filters.is_crossed is True:
            filter_is_crossed = models.SurveyA.is_crossed == True
        else:
            filter_is_crossed = models.SurveyA.is_crossed == False

        if filters.round:
            filter_round = models.SurveyA.vaccine_round == filters.round
        else:
            filter_round = self.model.id

        if filters.is_pregnant is None:
            filter_is_pregnant = self.model.id
        elif filters.is_pregnant is True:
            filter_is_pregnant = models.SurveyA.is_pregnant == True
        else:
            filter_is_pregnant = models.SurveyA.is_pregnant == False

        if filters.is_underlying_disease is None:
            filter_is_underlying_disease = self.model.id
        elif filters.is_underlying_disease is True:
            filter_is_underlying_disease = models.SurveyA.is_underlying_disease == True
        else:
            filter_is_underlying_disease = models.SurveyA.is_underlying_disease == False

        query = db.query(self.model).\
            filter(filter_query).filter(filter_age).filter(filter_gender).filter(filter_vaccine_type).\
            filter(filter_is_crossed).filter(filter_round).filter(filter_is_pregnant).filter(filter_is_underlying_disease).\
            group_by(self.model.id)

        page = page_request.get("page", 1)
        size = page_request.get("size", 10)

        return paginated_query(
            page_request,
            query,
            lambda x: x.order_by(self.model.id.desc()).limit(size).offset((page - 1) * size).all()
        )


review = CRUDReview(Review)
