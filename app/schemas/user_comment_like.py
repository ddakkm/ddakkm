from pydantic import BaseModel, EmailStr


class UserCommentLikeBase(BaseModel):
    pass


class UserCommentLikeCreate(UserCommentLikeBase):
    pass


class UserCommentLikeUpdate(UserCommentLikeBase):
    pass


class UserCommentLike(UserCommentLikeBase):
    user_id: int
    review_id: int

    class Config:
        orm_mode = True
