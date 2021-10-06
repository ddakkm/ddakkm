from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.users import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.user import nickname_randomizer


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # TODO : nickname_randomizer 실행 전 이메일 중복등 validation 필요
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            sns_provider=obj_in.sns_provider,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            join_survey_code=obj_in.join_survey_code,
            gender=obj_in.gender,
            age=obj_in.age,
            nickname=nickname_randomizer()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.email == email).first()

    def authentication(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(User)