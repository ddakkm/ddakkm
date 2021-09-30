from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.schemas.survey import SurveyACreate


class Images(BaseModel):
    image1_url: str = "http//sample.com/1"
    image2_url: str = "http//sample.com/2"
    image3_url: str = "http//sample.com/3"
    image4_url: str = "http//sample.com/4"
    image5_url: str = "http//sample.com/5"


class ReviewBase(BaseModel):
    writer_id: int
    content: Optional[str] = " asdasd "
    images: Optional[Images]


class ReviewCreateParams(ReviewBase):
    survey: SurveyACreate


class ReviewCreate(ReviewBase):
    survey_id: int


class ReviewUpdate(ReviewBase):
    survey: SurveyACreate