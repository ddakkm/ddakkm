import re

from fastapi import FastAPI, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.controllers.route import api_router

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url="/openapi.json", docs_url="/openapi.admin", redoc_url=None
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def index():
    return "hello"
