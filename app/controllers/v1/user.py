from typing import Any

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Body, HTTPException

from app.controllers import deps
from app import crud, schemas, models

router = APIRouter()


# TODO: ADD docs
@router.post("/join_survey")
async def create_join_survey(
        *,
        survey_in: schemas.SurveyCreate = Body(..., examples=schemas.survey_details_example),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    if current_user.join_survey_code != models.JoinSurveyCode.NONE:
        raise HTTPException(400, "이미 회원가입 설문을 마친 회원입니다.")
    return crud.user.create_join_survey(db=db, survey_in=survey_in, user_id=current_user.id)


@router.get("/me")
async def get_me(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return


@router.get("/{user_id}")
async def get_user_info(
        *,
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return


@router.post("/keyword")
async def set_keyword(
        *,
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return
