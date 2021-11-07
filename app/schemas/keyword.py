from typing import List

from pydantic import BaseModel


class KeywordBase(BaseModel):
    # TODO validation
    keywords: List[str] = ["심근염/심낭염"]


class UserKeywordCreate(KeywordBase):
    pass


class UserKeywordUpdate(BaseModel):
    keyword: str
    user_id: int


class ReviewKeywordUpdate(BaseModel):
    keyword: str
    review_id: int
