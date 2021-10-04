import re

from fastapi import FastAPI, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.controllers.route import api_router
from app.utils.user import open_nickname_csv, make_nickname_list, nicknames

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


@app.on_event("startup")
def startup_event():
    lines = open_nickname_csv("./app/nickname_csv.csv")
    make_nickname_list(lines, nicknames)


@app.get("/")
def index():
    return "hello"
