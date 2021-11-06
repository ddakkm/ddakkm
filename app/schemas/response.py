from typing import Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None
    error: Optional[str] = None
