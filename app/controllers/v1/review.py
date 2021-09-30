from typing import Any

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.controllers import deps
from app import crud, schemas


router = APIRouter()


@router.post("")
async def create_review(
        *,
        db: Session = Depends(deps.get_db),
        review_in: schemas.ReviewCreateParams
) -> Any:
    return crud.review.create(db, obj_in=review_in)