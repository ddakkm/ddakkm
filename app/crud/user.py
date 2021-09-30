from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users import User
from app.schemas.user import UserCreateParams, UserUpdate


class CRUDUser(CRUDBase[User, UserCreateParams, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreateParams) -> User:
        db_obj = User(
            sns_provider=obj_in.sns_provider,
            email=obj_in.email,
            join_survey_code=obj_in.join_survey_code,
            gender=obj_in.gender,
            age=obj_in.age,
            nickname="asdasd"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)