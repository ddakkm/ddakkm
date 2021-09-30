from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.users import SnsProviderType, Gender, JoinSurveyCode


class UserBase(BaseModel):
    sns_provider: SnsProviderType = SnsProviderType.LOCAL
    email: EmailStr = "sample@sample.com"
    gender: Gender = Gender.ETC
    age: int = 1980
    join_survey_code: JoinSurveyCode = JoinSurveyCode.NONE


class UserCreateParams(UserBase):
    pass


class UserUpdate(UserBase):
    pass
