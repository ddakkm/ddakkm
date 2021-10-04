from typing import Any, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.controllers import deps
from app.utils.review import symtom_randomizer
from app import crud, schemas

router = APIRouter()


@router.post("")
async def create_review(
        *,
        db: Session = Depends(deps.get_db),
        review_in: schemas.ReviewCreate
) -> Any:
    return crud.review.create(db, obj_in=review_in)


# @router.get("", response_model=List[schemas.Review])
@router.get("", response_model=List[schemas.ReviewResponse])
async def get_reviews(
        *,
        db: Session = Depends(deps.get_db)
) -> Any:
    review_list = [schemas.ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        nickname=review.user.nickname,
        vaccine_round=review.survey.vaccine_round,
        vaccine_type=review.survey.vaccine_type,
        symptom=symtom_randomizer(review.survey.data),
        content=review.content,
        like_count=review.like_count,
        comment_count=0
    ) for review in crud.review.get_multi(db)]
    return review_list
