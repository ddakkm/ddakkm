from app.crud.base import CRUDBase
from app.models.surveys import SurveyA
from app.schemas.survey import SurveyACreate, SurveyAUpdated


class CRUDSurveyA(CRUDBase[SurveyA, SurveyACreate, SurveyAUpdated]):
    pass


survey_a = CRUDSurveyA(SurveyA)