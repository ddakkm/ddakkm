from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings


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


@app.get("/")
def index():
    return "hello"