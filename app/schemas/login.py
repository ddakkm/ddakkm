from typing import Optional

from pydantic import BaseModel


class LoginResponse(BaseModel):
    is_user: bool
    access_token: Optional[str]
