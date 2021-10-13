from typing import Any

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.controllers import deps
from app import crud, schemas, models

router = APIRouter()


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
