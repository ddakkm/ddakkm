import re

from fastapi import FastAPI, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.models import Tag


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


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def index():
    return "hello"


@app.get("/test")
def test(db: Session = Depends(get_db)):
    return db.query(Tag).first()


@app.post('/my-endpoint')
def my_endpoint(request: Request):
    ip = request.client.host
    real_ip = request.headers.raw[2][1]
    return {"displayed_ip": ip, "x-real-ip": real_ip}
