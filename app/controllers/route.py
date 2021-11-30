from fastapi import APIRouter, Depends

from app.controllers import deps
from app.controllers.v1 import (
    user, review, auth, comment, qna
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth",tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
# api_router.include_router(user.router, prefix="/user", tags=["user"], dependencies=[Depends(deps.get_current_user)])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(comment.router, prefix="/comment", tags=["comment"])
api_router.include_router(qna.router, prefix="/qna", tags=["qna"])