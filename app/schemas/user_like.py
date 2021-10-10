from pydantic import BaseModel, EmailStr

from app.models.users import SnsProviderType, Gender, JoinSurveyCode


class UserLikeBase(BaseModel):
    pass


class UserCreate(UserLikeBase):
    pass


class UserUpdate(UserLikeBase):
    pass


class User(UserLikeBase):
    user_id: int
    review_id: int

    class Config:
        orm_mode = True
