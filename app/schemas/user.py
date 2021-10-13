from pydantic import BaseModel, EmailStr

from app.models.users import SnsProviderType, Gender, JoinSurveyCode


class UserBase(BaseModel):
    sns_provider: SnsProviderType = SnsProviderType.LOCAL
    gender: Gender = Gender.ETC
    age: int = 1980
    join_survey_code: JoinSurveyCode = JoinSurveyCode.NONE


class UserCreate(UserBase):
    password: str
    email: EmailStr = "sample@sample.com"


class UserUpdate(UserBase):
    password: str
    email: EmailStr = "sample@sample.com"


class SNSUserCreate(UserBase):
    pass


class SNSUserUpdate(UserBase):
    pass


class OauthLogin(BaseModel):
    sns_provider: SnsProviderType
    sns_access_token: str


class User(UserBase):
    nickname: str

    class Config:
        orm_mode = True
