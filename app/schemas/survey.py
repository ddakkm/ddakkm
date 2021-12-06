from enum import Enum
from typing import Union, Optional, List, Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator

from app.models.surveys import VaccineType, VaccineRound, DATE_FROM


# Survey type for join_survey -> 얘로 입력 받고 검증은 위에 애들로 함
class SurveyType(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class SurveyAData(BaseModel):
    q1: List[Union[int, str]] = [1]
    q2: List[int] = [1]
    q2_1: List[Any] = []
    q3: List[Union[int, str]] = [1]
    q4: List[Union[int, str]] = [1]
    q5: List[int] = [1]

    @validator("q1")
    def limit_q1_range(cls, v):
        str_val = len([value for value in v if isinstance(value, str)])
        if str_val > 1:
            raise TypeError(f"A 타입 설문지 q1 설문은 2개 이상의 String 타입 답변을 가질 수 없습니다. "
                            f"| length of string value in subjected list q1: {str_val}")
        if len(v) > 8:
            raise ValueError(f"A 타입 설문지 q1 설문의 가능한 최대 답변 갯수는 8개 (1번~7번 + 자유입력 1개) 입니다. "
                             f"| length of subjected list of q1:  {len(v)}")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 8):
                    raise ValueError(f"A 타입 설문지의 q1 설문의 번호 답변의 범위는 1번~7번 까지 입니다. | ValueError from {value}")
        return v

    @validator("q2")
    def limit_q2_range(cls, v):
        if len(v) > 1:
            raise ValueError(f"A 타입 설문지 q2 설문의 가능한 최대 답변 갯수는 1개 입니다."
                             f"| length of subjected list of q2: {len(v)}")
        if v[0] not in range(1, 7):
            raise ValueError(f"A 타입 설문지의 q2 설문의 번호 답변의 범위는 1번~6번 까지 입니다. | ValueError from {v}")
        return v

    @validator("q2_1")
    def limit_q2_1_range(cls, v, values):
        q2 = values.get("q2")
        if q2 == 1 and len(v) != 0:
            raise ValueError("q2의 답변이 1번이었다면 q2는 빈 배열이어야 합니다 (\"q2\": [])")
        if len(v) > 1:
            raise ValueError(f"A 타입 설문지 q2_1 설문의 가능한 최대 답변 갯수는 1개 입니다."
                             f"| length of subjected list of q2_1: {len(q2)}")
        if len(v) == 1:
            if v[0] not in range(1, 5) and v is not None:
                raise ValueError(f"A 타입 설문지의 q2_1 설문의 번호 답변의 범위는 1번~4번 까지 입니다. | ValueError from {v}")
        return v

    # 3번 질문 > 1~4번 답변 혹은 string
    @validator("q3")
    def limit_q3_range(cls, v):
        str_val = len([value for value in v if isinstance(value, str)])
        if str_val > 1:
            raise TypeError(f"A 타입 설문지 q3 설문은 2개 이상의 String 타입 답변을 가질 수 없습니다. "
                            f"| length of string value in subjected list q1: {str_val}")
        if len(v) > 5:
            raise ValueError(f"A 타입 설문지 q3 설문의 가능한 최대 답변 갯수는 5개 (1번~4번 + 자유입력 1개) 입니다. "
                             f"| length of subjected list of q1:  {len(v)}")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 5):
                    raise ValueError(f"A 타입 설문지의 q1 설문의 번호 답변의 범위는 1번~4번 까지 입니다. | ValueError from {value}")
        return v

    # 4번 질문 > 1~5번 답변 혹은 string
    @validator("q4")
    def limit_q4_range(cls, v):
        str_val = len([value for value in v if isinstance(value, str)])
        if str_val > 1:
            raise TypeError(f"A 타입 설문지 q4 설문은 2개 이상의 String 타입 답변을 가질 수 없습니다. "
                            f"| length of string value in subjected list q1: {str_val}")
        if len(v) > 6:
            raise ValueError(f"A 타입 설문지 q4 설문의 가능한 최대 답변 갯수는 6개 (1번~5번 + 자유입력 1개) 입니다. "
                             f"| length of subjected list of q1:  {len(v)}")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 6):
                    raise ValueError(f"A 타입 설문지의 q4 설문의 번호 답변의 범위는 1번~5번 까지 입니다. | ValueError from {value}")
        return v

    # 5번 질문 > 1~4번 답변
    @validator("q5")
    def limit_q5_range(cls, v):
        if len(v) > 1:
            raise ValueError(f"A 타입 설문지 q2 설문의 가능한 최대 답변 갯수는 1개 입니다."
                             f"| length of subjected list of q2: {len(v)}")
        if v[0] not in range(1, 5):
            raise ValueError(f"A 타입 설문지의 q5 설문의 번호 답변의 범위는 1번~4번 까지 입니다. | ValueError from {v}")
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


# Survey B type for join_survey
class SurveyBBase(BaseModel):
    q1: List[Union[int, str]] = [1]
    q2: List[int]

    @validator("q1")
    def limit_q1_range(cls, v):
        str_val = len([value for value in v if isinstance(value, str)])
        if str_val > 1:
            raise TypeError(f"B 타입 설문지 q1 설문은 2개 이상의 String 타입 답변을 가질 수 없습니다. "
                            f"| length of string value in subjected list q1: {str_val}")
        if len(v) > 5:
            raise ValueError(f"B 타입 설문지 q1 설문의 가능한 최대 답변 갯수는 5개 (1번~4번 + 자유입력 1개) 입니다. "
                             f"| length of subjected list of q1:  {len(v)}")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 5):
                    raise ValueError(f"B 타입 설문지의 q1 설문의 번호 답변의 범위는 1번~4번 까지 입니다. | ValueError from {value}")
        return v

    @validator("q2")
    def limit_q2_range(cls, v):
        if len(v) > 5:
            raise ValueError(f"B 타입 설문지 q2 설문의 가능한 최대 답변 갯수는 5개 (1번~5번) 입니다. | length of subjected list of q1:  {len(v)}")
        for value in v:
            if value not in range(1, 6):
                raise ValueError(f"B 타입 설문지의 q2 설문의 번호 답변의 범위는 1번~5번 까지 입니다. | ValueError from {value}")
        return v


class SurveyBCreate(SurveyBBase):
    pass


class SurveyBUpdate(SurveyBBase):
    pass


class SurveyB(SurveyBBase):
    pass

    class Config:
        orm_mode = True


# Survey C type for join_survey
class SurveyCBase(BaseModel):
    q1: List[Union[int, str]] = [1]
    q2: List[int]

    @validator("q1")
    def limit_q1_range(cls, v):
        str_val = len([value for value in v if isinstance(value, str)])
        if str_val > 1:
            raise TypeError(f"C 타입 설문지 q1 설문은 2개 이상의 String 타입 답변을 가질 수 없습니다. "
                            f"| length of string value in subjected list q1: {str_val}")
        if len(v) > 6:
            raise ValueError(f"C 타입 설문지 q1 설문의 가능한 최대 답변 갯수는 6개 (1번~5번 + 자유입력 1개) 입니다. "
                             f"| length of subjected list of q1:  {len(v)}")
        for value in v:
            if isinstance(value, str) is False:
                if value not in range(1, 6):
                    raise ValueError(f"C 타입 설문지의 q1 설문의 번호 답변의 범위는 1번~5번 까지 입니다. | ValueError from {value}")
        return v

    @validator("q2")
    def limit_q2_range(cls, v):
        if len(v) > 5:
            raise ValueError(f"C 타입 설문지 q2 설문의 가능한 최대 답변 갯수는 5개 (1번~5번) 입니다. | length of subjected list of q1:  {len(v)}")
        for value in v:
            if value not in range(1, 6):
                raise ValueError(f"C 타입 설문지의 q2 설문의 번호 답변의 범위는 1번~5번 까지 입니다. | ValueError from {value}")
        return v


class SurveyCCreate(SurveyCBase):
    pass


class SurveyCUpdate(SurveyCBase):
    pass


class SurveyC(SurveyCBase):
    pass

    class Config:
        orm_mode = True


class SurveyBase(BaseModel):
    survey_type: SurveyType = SurveyType.A
    survey_details: Any                         # survey_details 의 타입은 밸리데이션 단계에서 주입

    @validator("survey_details")
    def check_survey_form(cls, v, values):
        if values.get("survey_type") == SurveyType.A:
            v = SurveyACreate(**jsonable_encoder(v))
            return v

        if values.get("survey_type") == SurveyType.B:
            v = SurveyBCreate(**jsonable_encoder(v))
            return v

        if values.get("survey_type") == SurveyType.C:
            v = SurveyCCreate(**jsonable_encoder(v))
            return v


class ReviewDetail(BaseModel):
    content: str
    images: Optional[dict]
    keywords: List[str]


class SurveyCreate(SurveyBase):
    review_detail: ReviewDetail


class SurveyUpdate(SurveyBase):
    pass


class Survey(SurveyBase):

    class Config:
        orm_mode = True


survey_details_example = {
            "A": {
                "summary": "A 타입 설문지 예시",
                "description": "A 타입 설문지 예시",
                "value": {
                  "survey_type": "A",
                  "survey_details": {
                    "vaccine_type": "ETC",
                    "vaccine_round": "FIRST",
                    "is_crossed": False,
                    "is_pregnant": False,
                    "is_underlying_disease": False,
                    "date_from": "ZERO_DAY",
                    "data": {
                      "q1": [1, 2, 3, 4, 5, 6, 7, "근육통 이요? 근육이 애초에 없었는데요"],
                      "q2": [2],
                      "q2_1": [2],
                      "q3": [1, 2, 3, 4, "두통이요? 저는 머리가 없습니다."],
                      "q4": [1, 2, 3, 4, 5, "속이요? 저는 다이어터인데요."],
                      "q5": [1]
                    }
                  },
                  "review_detail": {
                    "content": "가입설문 예시",
                    "images": {
                      "image1_url": "https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/images/32c6f15b-3c50-59b3-8d3a-e98bfc223517.jpeg",
                      "image2_url": "https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/images/236920af-3da9-5fe6-a4ee-e5abbe8dffa5.heic",
                      "image3_url": "https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/images/1ae135a7-a58d-59b8-90a3-a6471abac265.heic"
                      },
                    "keywords": ["심근염/심낭염"]
                    }
                }
            },
            "B": {
                "summary": "B 타입 설문지 예시",
                "description": "B 타입 설문지 예시",
                "value": {
                  "survey_type": "B",
                  "survey_details": {
                    "q1": [1, 2, 3, 4, "엄마가 하래서"],
                    "q2": [1, 2, 3]
                  }
                }
            },
            "C": {
                "summary": "C 타입 설문지 예시",
                "description": "C 타입 설문지 예시",
                "value": {
                  "survey_type": "C",
                  "survey_details": {
                    "q1": [1, 2, 3, 4, 5, "엄마가 하지 말래서"],
                    "q2": [1, 2, 3]
                  }
                }
            }
}
