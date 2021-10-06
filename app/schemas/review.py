from typing import Optional, Union

from pydantic import BaseModel

from app.schemas.survey import SurveyACreate, SurveyA
from app.schemas.user import User


class Images(BaseModel):
    image1_url: str = "http//sample.com/1"
    image2_url: Optional[str]
    image3_url: Optional[str]
    image4_url: Optional[str]
    image5_url: Optional[str]


class ReviewBase(BaseModel):
    content: Optional[str] = " asdasd "
    images: Optional[Images]


# 리뷰 작성시 입력해야할 파라미터로 설문양식 A를 포함합니다.
class ReviewCreate(ReviewBase):
    survey: SurveyACreate


class ReviewUpdate(ReviewBase):
    survey: SurveyACreate


class Review(ReviewBase):
    user_id: int
    survey: SurveyA
    user: User

    class Config:
        orm_mode = True


# Review Model for API Response
class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    nickname: str
    vaccine_round: str
    vaccine_type: str
    symptom: dict
    content: str
    like_count: int
    comment_count: int
