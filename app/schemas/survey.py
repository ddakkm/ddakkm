from enum import Enum
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
        if len(v) > 9:
            raise ValueError("Out of Range")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 8):
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


class SurveyBBase(BaseModel):
    pass


class SurveyBCreate(SurveyBBase):
    pass


class SurveyCBase(BaseModel):
    pass


class SurveyCCreate(SurveyBBase):
    pass


class SurveyType(str, Enum):
    A = "A"
    B = "B"
    C = "C"


# TODO survey_details Validation
class SurveyCreate(BaseModel):
    survey_type: SurveyType = SurveyType.A
    survey_details: dict


class Survey(SurveyCreate):
    pass


survey_details_example = {
            "A": {
                "summary": "A 타입 설문지 예시",
                "description": "A 타입 설문지 예시",
                "value": {
                    "content": "복통이 심했어요",
                    "images": {
                        "image1_url": "http://sample.com/1",
                        "image2_url": "http://sample.com/2",
                        "image3_url": "http://sample.com/3",
                        "image4_url": "http://sample.com/4",
                        "image5_url": "http://sample.com/5"
                        },
                    "survey": {
                        "survey_type": "A",
                        "survey_details": {
                          "vaccine_type": "ETC",
                          "vaccine_round": "FIRST",
                          "is_crossed": False,
                          "is_pregnant": False,
                          "is_underlying_disease": False,
                          "date_from": "ZERO_DAY",
                          "data": {
                            "q1": [
                              1, 2, "콧등 근육쪽에 심한 근육통이 있었습니다."
                            ],
                            "q2": 2,
                            "q2_1": 2,
                            "q3": 1,
                            "q4": [
                              1
                            ],
                            "q5": 1
                          }
                        },
                    }
                }
            },
            "B": {
                "summary": "B 타입 설문지 예시",
                "description": "B 타입 설문지 예시",
                "value": {
                    "TODO": "TODO"
                },
            },
            "C": {
                "summary": "C 타입 설문지 예시",
                "description": "C 타입 설문지 예시",
                "value": {
                    "TODO": "TODO"
                },
            }
}
