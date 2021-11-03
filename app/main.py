from logging.config import dictConfig
import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.controllers.route import api_router
from app.utils.user import open_nickname_csv, make_nickname_list, nicknames

# TODO 로깅 설정 다른곳으로 옮기기 // logger에 실제 IP 주소 넣기
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s [ddakkm_api] %(asctime)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "ddakkm_logger": {"handlers": ["default"], "level": "DEBUG"},
        "sqlalchemy.engine": {"handlers": ["default"], "level": "INFO"}
    },
}
dictConfig(log_config)


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
    # normal
    lines = open_nickname_csv("./app/nickname_csv.csv")

    # debug
    # lines = open_nickname_csv("../app/nickname_csv.csv")
    make_nickname_list(lines, nicknames)


@app.get("/")
def index():
    return "hello"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)