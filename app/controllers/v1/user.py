from typing import Any

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.controllers import deps
from app import crud, schemas

router = APIRouter()


# @router.post("")
# async def create_user(
#         *,
#         db: Session = Depends(deps.get_db),
#         user_in: schemas.UserCreate
# ) -> Any:
#     return crud.user.create(db, obj_in=user_in)