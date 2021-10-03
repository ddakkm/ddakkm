from typing import Any, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.controllers import deps
from app import crud, schemas
from app.utils.user import nicknames

router = APIRouter()


@router.post("")
async def create_review(
        *,
        db: Session = Depends(deps.get_db),
        review_in: schemas.ReviewCreate
) -> Any:
    return crud.review.create(db, obj_in=review_in)


@router.get("", response_model=List[schemas.Review])
async def get_reviews(
        *,
        db: Session = Depends(deps.get_db)
) -> Any:
    return crud.review.get_multi(db)


@router.get("/test")
async def test():
    return nicknames[3865]