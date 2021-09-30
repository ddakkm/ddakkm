from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.schemas.survey import SurveyACreate


class Images(BaseModel):
    image1_url: Optional[HttpUrl]
    image2_url: Optional[HttpUrl]
    image3_url: Optional[HttpUrl]
    image4_url: Optional[HttpUrl]
    image5_url: Optional[HttpUrl]


class ReviewBase(BaseModel):
    writer_id: int
    survey_id: int
    content: Optional[str] = " asdasd "
    images: Optional[Images]


class ReviewCreate(ReviewBase):
    survey: SurveyACreate


class ReviewUpdate(ReviewBase):
    survey: SurveyACreate