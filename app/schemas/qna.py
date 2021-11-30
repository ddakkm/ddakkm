from typing import Optional

from pydantic import BaseModel


class QnaBase(BaseModel):
    content: str
    user_email: Optional[str] = "ddakkm@gmail.com"
    user_phone: Optional[str] = "010-3333-4444"


class QnaCreate(QnaBase):
    pass


class QnaUpdate(QnaBase):
    pass


class Qna(QnaBase):
    is_solved: bool
    user_id: int
    id: int