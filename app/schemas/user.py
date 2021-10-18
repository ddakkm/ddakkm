from pydantic import BaseModel, EmailStr

from app.models.users import SnsProviderType, Gender, JoinSurveyCode


class UserBase(BaseModel):
    gender: Gender = Gender.ETC
    age: int = 1980


class UserCreate(UserBase):
    password: str
    email: EmailStr = "sample@sample.com"
    agree_over_fourteen: bool = True
    agree_privacy_policy: bool = True


class UserUpdate(UserBase):
    password: str
    email: EmailStr = "sample@sample.com"


class SNSUserCreate(UserBase):
    agree_over_fourteen: bool = True
    agree_privacy_policy: bool = True


class SNSUserUpdate(UserBase):
    pass


class OauthIn(BaseModel):
    sns_provider: SnsProviderType
    sns_access_token: str


class User(UserBase):
    nickname: str
    join_survey_code: JoinSurveyCode = JoinSurveyCode.NONE
    sns_provider: SnsProviderType = SnsProviderType.LOCAL

    class Config:
        orm_mode = True
