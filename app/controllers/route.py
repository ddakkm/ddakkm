from fastapi import APIRouter

from app.controllers.v1 import (
    user, review
)

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
