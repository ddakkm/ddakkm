from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.users import User, JoinSurveyCode, SnsProviderType
from app.schemas.user import UserCreate, UserUpdate, SNSUserCreate, OauthIn
from app.utils.user import nickname_randomizer


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
            agree_privacy_policy=obj_in.agree_privacy_policy,
            agree_over_fourteen=obj_in.agree_over_fourteen
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
            sns_id=sns_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.email == email).first()

    def authentication(self, db: Session, *, email: str, password: str) -> Optional[User]:
        local_user = self.get_by_email(db, email=email)
        if not local_user:
            return None
        if not verify_password(password, local_user.hashed_password):
            return None
        return local_user

    def get_by_sns_id(self, db: Session, *, sns_id: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.sns_id == sns_id).first()


user = CRUDUser(User)
