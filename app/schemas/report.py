from pydantic import BaseModel, validator


class ReportReason(BaseModel):
    reason: int

    @validator("reason")
    def limit_reason_range(cls, v):
        if not 0 < v < 5:
            raise ValueError("신고 사유의 범위는 1~4 사이의 integer 값 입니다.")
        return v
