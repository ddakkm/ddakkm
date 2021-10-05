from typing import Union, Optional, List

from pydantic import BaseModel, validator

from app.models.surveys import VaccineType, VaccineRound, DATE_FROM


class SurveyAData(BaseModel):
    q1: List[Union[int, str]] = [1]
    q2: int = 1
    q2_1: Optional[int] = None
    q3: Union[int, str] = 1
    q4: List[Union[int, str]] = [1]
    q5: int = 1

    # 1번 질문 > 답변의 요소가 7개 이상일 수 없음
    # 1번 질문 > 1~6번 답변 혹은 string
    @validator("q1")
    def limit_q1_range(cls, v):
        if len(v) > 7:
            raise ValueError("Out of Range")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 7):
                    raise ValueError("Out Of Range")
        return v

    # 2번 질문 > 1~6번 답변
    @validator("q2")
    def limit_q2_range(cls, v):
        if v not in range(1, 7):
            raise ValueError("Out Of Range")
        return v

    # 2번 질문이 1일때 > 2-1번 질문에는 답변이 없어야함
    # 2번 질문이 1이 아닐때 > 2-1번의 답변은 None이면 안되고 1~4이어야 함
    @validator("q2_1")
    def limit_q2_1_range(cls, v, values):
        q2 = values.get("q2")
        if q2 == 1 and v is not None:
            raise ValueError("if answer of q2 is 1, q2_1 needs to be None")
        if v not in range(1, 5) and v is not None:
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
        if len(v) > 6:
            raise ValueError("Out of Range")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1,6):
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
    vaccine_type: VaccineType = VaccineType.ETC
    vaccine_round: VaccineRound = VaccineRound.FIRST
    is_crossed: bool = False
    is_pregnant: bool = False
    is_underlying_disease: bool = False
    date_from: DATE_FROM = DATE_FROM.ZERO_DAY
    data: SurveyAData


class SurveyACreate(SurveyABase):
    pass


class SurveyAUpdated(SurveyABase):
    user_id: int


class SurveyA(SurveyABase):
    user_id: int

    class Config:
        orm_mode = True
