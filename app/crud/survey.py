from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.surveys import SurveyA, SurveyB, SurveyC
from app.schemas.survey import SurveyACreate, SurveyAUpdated, SurveyBCreate, SurveyBUpdate, SurveyCCreate, SurveyCUpdate


# For Review Create (리뷰 작성시에는 A 타입만 허용)
class CRUDSurveyA(CRUDBase[SurveyA, SurveyACreate, SurveyAUpdated]):
    pass


class CRUDSurveyB(CRUDBase[SurveyB, SurveyBCreate, SurveyBUpdate]):
    pass


class CRUDSurveyC(CRUDBase[SurveyB, SurveyBCreate, SurveyBUpdate]):
    pass


survey_a = CRUDSurveyA(SurveyA)
survey_b = CRUDSurveyB(SurveyB)
survey_c = CRUDSurveyC(SurveyC)