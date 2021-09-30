from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.surveys import SurveyA
from app.schemas.survey import SurveyACreate, SurveyAUpdated


class CRUDReview(CRUDBase[SurveyA, SurveyACreate, SurveyAUpdated]):
    pass


survey_a = CRUDReview(SurveyA)