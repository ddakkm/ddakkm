from typing import List
import logging

from sqlalchemy.orm import Session, joinedload, aliased
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from app import models
from app.crud.base import CRUDBase
from app.crud.survey import survey_a
from app.models.reviews import Review, ReviewKeyword
from app.models.users import User, UserKeyword
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewParams
from app.schemas.survey import SurveyA
from app.schemas.page_response import paginated_query
from app.utils.user import calculate_birth_year_from_age


logger = logging.getLogger('ddakkm_logger')


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def create_no_commit(self, db: Session, *, obj_in: ReviewCreate) -> Review:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        return db_obj

    def create_by_current_user(self, db: Session, *, obj_in: ReviewCreate, user_id: int):
        # 리뷰 작성을 위한 요청 바디에 포함되어있는 user_id로 서베이를 등록한다.
        survey_create_schema = SurveyA(**jsonable_encoder(obj_in.survey), user_id=user_id)
        survey_id = survey_a.create(db=db, obj_in=survey_create_schema).id

        # 이미지 유무에 따라 입력값 결정
        if obj_in.images is None:
            db_obj = self.model(
                user_id=user_id,
                survey_id=survey_id,
                content=obj_in.content
            )
        else:
            db_obj = self.model(
                user_id=user_id,
                survey_id=survey_id,
                content=obj_in.content,
                images=jsonable_encoder(obj_in.images)
            )
        db.add(db_obj)
        db.flush()
        return db_obj

    def get_list_paginated(self, db: Session, page_request: dict, filters: ReviewParams) -> List[Review]:
        if filters.q:
            filter_query = self.model.content.contains(filters.q)
        else:
            filter_query = self.model.id

        if filters.min_age and filters.max_age:
            min_birth_year = calculate_birth_year_from_age(filters.min_age)
            max_birth_year = calculate_birth_year_from_age(filters.max_age)
            filter_age = models.User.age.between(max_birth_year, min_birth_year)
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

        query = db.query(self.model).outerjoin(models.SurveyA).options(joinedload(self.model.survey)).\
            join(models.User).options(joinedload(self.model.user)).\
            filter(filter_query).filter(filter_age).filter(filter_gender).filter(filter_vaccine_type).\
            filter(filter_is_crossed).filter(filter_round).filter(filter_is_pregnant).\
            filter(filter_is_underlying_disease).filter(self.model.is_delete == False).\
            filter(models.User.is_active == True).\
            group_by(self.model.id)

        page = page_request.get("page", 1)
        size = page_request.get("size", 20)

        return paginated_query(
            page_request,
            query,
            lambda x: x.order_by(self.model.id.desc()).limit(size).offset((page - 1) * size).all()
        )

    def get_review(self, db: Session, id: int) -> Review:
        review_obj = db.query(self.model).filter(self.model.id == id).\
            join(models.User).options(joinedload(self.model.user)).\
            filter(models.User.is_active == True).first()
        if review_obj is None:
            raise HTTPException(404, "리뷰를 찾을 수 없습니다.")
        return review_obj

    @staticmethod
    def update_review(db: Session, *, db_obj: Review, obj_in: ReviewUpdate, current_user: User) -> Review:
        if db_obj.user_id != current_user.id:
            raise HTTPException(400, "이 게시글을 수정할 권한이 없습니다.")
        logger.info(f"리뷰 #{db_obj.id} 수정 요청 {jsonable_encoder(obj_in)}")
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def set_review_status_as_deleted(db: Session, *, db_obj: Review, current_user: User) -> Review:
        if current_user.is_super is True or db_obj.user_id == current_user.id:
            db_obj.is_delete = True
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            raise HTTPException(400, "이 게시글을 수정할 권한이 없습니다.")

    def get_review_details(self, db: Session, review_id: int) -> Review:
        review_user = aliased(models.User)
        review_obj = db.query(self.model).outerjoin(models.Comment).outerjoin(models.Comment.user).\
            options(joinedload(self.model.comments).joinedload(models.Comment.user)).\
            outerjoin(models.ReviewKeyword).options(joinedload(self.model.keywords)).\
            join(review_user, review_user.id == self.model.user_id).options(joinedload(self.model.user)).\
            filter(self.model.is_delete == False).filter(self.model.id == review_id).\
            filter(review_user.is_active == True).\
            first()

        if review_obj is None:
            raise HTTPException(404, "리뷰를 찾을 수 없습니다.")
        return review_obj

    def get_reviews_by_user_id(self, db: Session, user_id: int) -> List[Review]:
        result = db.query(self.model).filter(self.model.user_id == user_id).filter(self.model.is_delete == False).order_by(self.model.created_at.desc()).all()
        return result

    def get_reviews_by_ids(self, db: Session, ids: List[int]) -> List[Review]:
        result = db.query(self.model).filter(self.model.id.in_(ids)).all()
        return result

    def get_review_counts_by_user_id(self, db: Session, user_id: int) -> int:
        counts = db.query(self.model).filter(self.model.user_id == user_id).filter(self.model.is_delete == False).count()
        return counts

    def get_reviews_has_comment(self, db: Session):
        return db.query(self.model).join(models.Comment).all()


review = CRUDReview(Review)
