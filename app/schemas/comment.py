from typing import Optional, List

from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class NestedComment(CommentBase):
    id: int
    user_id: int
    nickname: str


class Comment(CommentBase):
    id: int
    user_id: int
    nickname: str
    nested_comment: Optional[List[NestedComment]]

    class Config:
        orm_mode = True
