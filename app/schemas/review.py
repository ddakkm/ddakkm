from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.schemas.survey import SurveyACreate, SurveyA
from app.schemas.user import User


class Images(BaseModel):
    image1_url: str = "http//sample.com/1"
    image2_url: str = "http//sample.com/2"
    image3_url: str = "http//sample.com/3"
    image4_url: str = "http//sample.com/4"
    image5_url: str = "http//sample.com/5"


class ReviewBase(BaseModel):
    user_id: int
    content: Optional[str] = " asdasd "
    images: Optional[Images]


# 리뷰 작성시 입력해야할 파라미터로 설문양식 A를 포함합니다.
class ReviewCreate(ReviewBase):
    survey: SurveyACreate


class ReviewUpdate(ReviewBase):
    survey: SurveyACreate


class Review(ReviewBase):
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
