from typing import List

from pydantic import BaseModel


class UserKeywordBase(BaseModel):
    # TODO validation
    keywords: List[str] = ["심근염/심낭염"]


class UserKeywordCreate(UserKeywordBase):
    pass
