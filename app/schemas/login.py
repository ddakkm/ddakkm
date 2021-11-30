from typing import Optional

from pydantic import BaseModel

from app.models.users import Gender, JoinSurveyCode, SnsProviderType


class LoginResponse(BaseModel):
    status: str = "OK"
    is_user: bool
    done_survey: Optional[bool]
    access_token: Optional[str]
    nickname: Optional[str]


class CreateSnsResponse(BaseModel):
    id: int
    gender: Gender
    sns_id: str
    age: int
    email: str
    join_survey_code: JoinSurveyCode
    is_super: bool
    is_active: bool
    sns_provider: SnsProviderType
    nickname: str
    access_token: str
    character_image: str

    class Config:
        orm_mode = True
