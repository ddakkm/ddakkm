from fastapi import APIRouter

from app.controllers.v1 import (
    user
)

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
