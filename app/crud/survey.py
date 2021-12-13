from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.users import User, JoinSurveyCode
from app.models.surveys import SurveyA, SurveyB, SurveyC
from app.schemas.survey import SurveyACreate, SurveyAUpdated, SurveyBCreate, SurveyBUpdate, SurveyCCreate, SurveyCUpdate


# For Review Create (리뷰 작성시에는 A 타입만 허용)
class CRUDSurveyA(CRUDBase[SurveyA, SurveyACreate, SurveyAUpdated]):
    def create_no_commit(self, db: Session, *, obj_in: SurveyACreate) -> SurveyA:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        return db_obj

    def get_join_survey(self, db: Session, user_id: int):
        return db.query(self.model).\
            filter(self.model.is_join_survey == True).\
            filter(self.model.user_id == user_id).first()


class CRUDSurveyB(CRUDBase[SurveyB, SurveyBCreate, SurveyBUpdate]):
    def get_join_survey(self, db: Session, user_id: int):
        return db.query(self.model).\
            filter(self.model.is_join_survey == True).\
            filter(self.model.user_id == user_id).first()


class CRUDSurveyC(CRUDBase[SurveyB, SurveyBCreate, SurveyBUpdate]):
    def get_join_survey(self, db: Session, user_id: int):
        return db.query(self.model).\
            filter(self.model.is_join_survey == True).\
            filter(self.model.user_id == user_id).first()


survey_a = CRUDSurveyA(SurveyA)
survey_b = CRUDSurveyB(SurveyB)
survey_c = CRUDSurveyC(SurveyC)
