from typing import Optional

from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    review_id: int
    user_id: int

    class Config:
        orm_mode = True
