from typing import Optional, List
from datetime import datetime

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
    created_at: datetime
    is_delete: bool


class Comment(CommentBase):
    id: int
    user_id: int
    nickname: str
    created_at: datetime
    nested_comment: Optional[List[NestedComment]]
    is_delete: bool

    class Config:
        orm_mode = True
