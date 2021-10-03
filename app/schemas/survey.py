from dataclasses import dataclass
from typing import Union

from pydantic import BaseModel, validator

from app.models.surveys import VaccineType, DATE_FROM


class SurveyAData(BaseModel):
    q1: Union[int, str] = 1
    q2: int = 1
    q2_1: int = 1
    q3: Union[int, str] = 1
    q4: Union[int, str] = 1
    q5: int = 1

    # 1번 질문 > 1~6번 답변 혹은 string
    @validator("q1")
    def limit_q1_range(cls, v):
        if isinstance(v, str) is False:
            if v not in range(1, 7):
                raise ValueError("Out Of Range")
        return v

    # 2번 질문 > 1~6번 답변
    @validator("q2")
    def limit_q2_range(cls, v):
        if v not in range(1, 7):
            raise ValueError("Out Of Range")
        return v

    # 2-1번 질문 > 1~4번 답변
    @validator("q2_1")
    def limit_q2_1_range(cls, v):
        if v not in range(1, 5):
            raise ValueError("Out Of Range")
        return v

    # 3번 질문 > 1~4번 답변 혹은 string
    @validator("q3")
    def limit_q3_range(cls, v):
        if isinstance(v, str) is False:
            if v not in range(1, 5):
                raise ValueError("Out Of Range")
        return v

    # 4번 질문 > 1~5번 답변 혹은 string
    @validator("q4")
    def limit_q4_range(cls, v):
        if isinstance(v, str) is False:
            if v not in range(1,6):
                raise ValueError("Out of Range")
        return v

    # 5번 질문 > 1~4번 답변
    @validator("q5")
    def limit_q5_range(cls, v):
        if v not in range(1,5):
            raise ValueError("Out of Range")
        return v


# 기본 설문 A 베이스 스키마
class SurveyABase(BaseModel):
    user_id: int
    vaccine_type: VaccineType = VaccineType.ETC
    is_crossed: bool = False
    is_pregnant: bool = False
    is_underlying_disease: bool = False
    date_from: DATE_FROM = DATE_FROM.ZERO_DAY
    data: SurveyAData


class SurveyACreate(SurveyABase):
    pass


class SurveyAUpdated(SurveyABase):
    pass


class SurveyA(SurveyABase):
    class Config:
        orm_mode = True
