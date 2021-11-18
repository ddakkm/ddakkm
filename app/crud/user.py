import random
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import crud, models, schemas
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.users import User, JoinSurveyCode, SnsProviderType, UserKeyword
from app.schemas.user import UserCreate, UserUpdate, SNSUserCreate, OauthIn
from app.schemas.keyword import UserKeywordCreate
from app.schemas.survey import SurveyType, SurveyCreate, SurveyA, SurveyB, SurveyC
from app.schemas.response import BaseResponse
from app.utils.user import nickname_randomizer, character_image_randomizer, character_images


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # TODO : nickname_randomizer 실행 전 이메일 중복등 validation 필요
    def create_local(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            sns_provider=SnsProviderType.LOCAL,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            join_survey_code=JoinSurveyCode.NONE,
            gender=obj_in.gender,
            age=obj_in.age,
            nickname=nickname_randomizer(),
            sns_id="LOCAL_USER",
            agree_policy=obj_in.agree_policy,
            character_image=character_image_randomizer(),
            agree_keyword_push=False,
            agree_activity_push=False,
            fcm_token=obj_in.fcm_token,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_sns(self, db: Session, *, obj_in: SNSUserCreate, oauth_in: OauthIn, sns_id: str) -> User:
        db_obj = self.model(
            sns_provider=oauth_in.sns_provider,
            email="",
            hashed_password="",
            join_survey_code=JoinSurveyCode.NONE,
            gender=obj_in.gender,
            age=obj_in.age,
            nickname=nickname_randomizer(),
            sns_id=sns_id,
            agree_policy=obj_in.agree_policy,
            character_image=character_image_randomizer(),
            agree_keyword_push=False,
            agree_activity_push=False,
            fcm_token=obj_in.fcm_token,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.email == email).first()

    def authentication(self, db: Session, *, email: str, password: str) -> Optional[User]:
        local_user = self.get_by_email(db, email=email)
        if not local_user or local_user.is_active is False:
            return None
        if not verify_password(password, local_user.hashed_password):
            return None
        return local_user

    def get_by_sns_id(self, db: Session, *, sns_id: str) -> Optional[User]:
        sns_user = db.query(self.model).filter(self.model.sns_id == sns_id).first()
        # if not sns_user or sns_user.is_active is False:
        #     raise HTTPException(401, "입력된 정보에 해당하는 유저를 찾을 수 없습니다.")
        return sns_user

    def create_join_survey(self, db: Session, survey_in: SurveyCreate, *, user_id: int) \
            -> User:
        # A 타입 설문지 -> 설문 내용을 작성 양식에 맞게 넣고, user_id 와 함께 입력 >> 빈 내용의 리뷰도 함께 생성
        if survey_in.survey_type == SurveyType.A:
            survey_create_schema = SurveyA(**jsonable_encoder(survey_in.survey_details), user_id=user_id)
            survey = crud.survey_a.create(db=db, obj_in=survey_create_schema)
            review_obj = models.Review(user_id=user_id, survey_id=survey.id, content=None)
            crud.review.create(db=db, obj_in=review_obj)
        # B 타입 설문지 -> 설문 내용을 작성 양식에 맞게 넣고, user_id 와 함께 DB에 입력
        elif survey_in.survey_type == SurveyType.B:
            survey_create_schema = SurveyB(**jsonable_encoder(survey_in.survey_details))
            crud.survey_b.create(db=db, obj_in=models.SurveyB(data=survey_create_schema, user_id=user_id))
        # C 타입 설문지 -> 설문 내용을 작성 양식에 맞게 넣고, user_id 와 함께 DB에 입력
        else:
            survey_create_schema = SurveyC(**jsonable_encoder(survey_in.survey_details))
            crud.survey_c.create(db=db, obj_in=models.SurveyC(data=survey_create_schema, user_id=user_id))

        # 유저 정보 업데이트
        db_obj = db.query(self.model).filter(self.model.id == user_id).first()
        db_obj.join_survey_code = survey_in.survey_type
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_by_user_id(self, db: Session, *, user_id: int) -> BaseResponse:
        user = db.query(self.model).filter(self.model.id == user_id).first()
        message = f"user from {user.sns_provider} | user_id: {user_id} \n is deleted" \
                  f"deleted comment : {len(user.comments)} || deleted reviews : {len(user.reviews)}"
        try:
            db.query(models.Comment).filter(models.Comment.user_id == user_id).delete()
            db.query(models.Review).filter(models.Review.user_id == user_id).delete()
            db.query(models.SurveyA).filter(models.SurveyA.user_id == user_id).delete()
            db.query(models.SurveyB).filter(models.SurveyB.user_id == user_id).delete()
            db.query(models.SurveyC).filter(models.SurveyC.user_id == user_id).delete()
            db.query(models.UserLike).filter(models.UserLike.user_id == user_id).delete()
            db.delete(user)
            db.commit()
            return BaseResponse(status="ok", message=message)
        except Exception as e:
            return BaseResponse(status="failed", error=str(e))

    def soft_delete_by_user_id(self, db: Session, user_id: int) -> BaseResponse:
        user = db.query(self.model).filter(self.model.id == user_id).first()
        now = datetime.now()
        user.is_active = False
        user.updated_at = now
        db.add(user)
        db.commit()
        db.refresh(user)
        return BaseResponse(message=f"유저 #{user.id}가 비활성화 되었습니다.", object=user_id)

    @staticmethod
    def change_user_agree_keyword_push_status(db: Session, current_user: User) -> schemas.BaseResponse:
        if current_user.agree_keyword_push is False:
            current_user.agree_keyword_push = True
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
            return schemas.BaseResponse(
                object=current_user.id, message=f"유저 ID : #{current_user.id}의 키워드 알림 수신 여부가 \"동의\"로 변경되었습니다."
            )
        else:
            current_user.agree_keyword_push = False
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
            return schemas.BaseResponse(
                object=current_user.id, message=f"유저 ID : #{current_user.id}의 키워드 알림 수신 여부가 \"거부\"로 변경되었습니다."
            )

    @staticmethod
    def change_user_agree_activity_push_status(db: Session, current_user: User) -> schemas.BaseResponse:
        if current_user.agree_activity_push is False:
            current_user.agree_activity_push = True
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
            return schemas.BaseResponse(
                object=current_user.id, message=f"유저 ID : #{current_user.id}의 활동 알림 수신 여부가 \"동의\"로 변경되었습니다."
            )
        else:
            current_user.agree_activity_push = False
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
            return schemas.BaseResponse(
                object=current_user.id, message=f"유저 ID : #{current_user.id}의 활동 알림 수신 여부가 \"거부\"로 변경되었습니다."
            )
        return current_user

    @staticmethod
    def create_keywords(db: Session, obj_in: UserKeywordCreate, user_id: int) -> List[UserKeyword]:
        db_obj = [UserKeyword(user_id=user_id, keyword=keyword) for keyword in obj_in.keywords]
        db.bulk_save_objects(db_obj)
        db.commit()
        return db_obj


user = CRUDUser(User)
