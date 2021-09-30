from pydantic import BaseModel

from app.models.surveys import VaccineType, DATE_FROM


class SurveyAData(BaseModel):
    q1: str = "asd"
    q2: str = "asd"
    q33: str = "asd"


# 기본 설문 A 베이스 스키마
class SurveyABase(BaseModel):
    user_id: int
    vaccine_type: VaccineType = VaccineType.ETC
    is_crossed: bool = False
    is_pregnant: bool = False
    is_underlying_disease: bool = False
    date_from: DATE_FROM = DATE_FROM.ZERO
    data: SurveyAData


class SurveyACreate(SurveyABase):
    pass


class SurveyAUpdated(SurveyABase):
    pass
