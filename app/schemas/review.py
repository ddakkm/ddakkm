from typing import Optional, List

from pydantic import BaseModel

from app.schemas.survey import Survey, VaccineType, VaccineRound, SurveyCreate
from app.schemas.user import User, Gender
from app.schemas.comment import Comment


class ReviewParams(BaseModel):
    q: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[Gender] = None
    vaccine_type: Optional[VaccineType] = None
    is_crossed: Optional[bool] = None
    round: Optional[VaccineRound] = None
    is_pregnant: Optional[bool] = None
    is_underlying_disease: Optional[bool] = None


class Images(BaseModel):
    image1_url: Optional[str] = "http//sample.com/1"
    image2_url: Optional[str]
    image3_url: Optional[str]
    image4_url: Optional[str]
    image5_url: Optional[str]


class ReviewBase(BaseModel):
    content: Optional[str] = " asdasd "
    images: Optional[Images]


# 리뷰 작성시 입력해야할 파라미터로 설문양식 A를 포함합니다.
class ReviewCreate(ReviewBase):
    survey: SurveyCreate


class ReviewUpdate(ReviewBase):
    pass


class Review(ReviewBase):
    id: int
    survey: Survey
    is_writer: bool
    user_id: int
    nickname: str
    comments: List[Comment]

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
    user_is_like: bool
