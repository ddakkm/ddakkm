from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users import User, JoinSurveyCode
from app.models.surveys import SurveyA, SurveyB, SurveyC
from app.schemas.survey import SurveyACreate, SurveyAUpdated, SurveyBCreate, SurveyBUpdate, SurveyCCreate, SurveyCUpdate


# For Review Create (리뷰 작성시에는 A 타입만 허용)
class CRUDSurveyA(CRUDBase[SurveyA, SurveyACreate, SurveyAUpdated]):
    def get_join_survey(self, db: Session, user_id: int):
        return db.query(self.model).\
            filter(self.model.is_join_survey == True).\
            filter(self.model.user_id == user_id).first()

    @staticmethod
    def delete_join_survey(db: Session, join_survey_model: SurveyA, user_model: User):
        db.delete(join_survey_model)
        db.flush()
        print(user_model.join_survey_code)
        user_model.join_survey_code = JoinSurveyCode.NONE
        print(user_model.join_survey_code)
        db.add(user_model)
        db.commit()
        db.refresh(user_model)
        db.close()


class CRUDSurveyB(CRUDBase[SurveyB, SurveyBCreate, SurveyBUpdate]):
    def get_join_survey(self, db: Session, user_id: int):
        return db.query(self.model).\
            filter(self.model.is_join_survey == True).\
            filter(self.model.user_id == user_id).first()

    @staticmethod
    def delete_join_survey(db: Session, join_survey_model: SurveyB, user_model: User):
        db.delete(join_survey_model)
        db.refresh(join_survey_model)
        user_model.join_survey_code = JoinSurveyCode.NONE
        db.add(user_model)
        db.refresh(user_model)
        db.commit()
        db.close()


class CRUDSurveyC(CRUDBase[SurveyB, SurveyBCreate, SurveyBUpdate]):
    def get_join_survey(self, db: Session, user_id: int):
        return db.query(self.model).\
            filter(self.model.is_join_survey == True).\
            filter(self.model.user_id == user_id).first()

    @staticmethod
    def delete_join_survey(db: Session, join_survey_model: SurveyC, user_model: User):
        db.delete(join_survey_model)
        db.refresh(join_survey_model)
        user_model.join_survey_code = JoinSurveyCode.NONE
        db.add(user_model)
        db.refresh(user_model)
        db.commit()
        db.close()


survey_a = CRUDSurveyA(SurveyA)
survey_b = CRUDSurveyB(SurveyB)
survey_c = CRUDSurveyC(SurveyC)
