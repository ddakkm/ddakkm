import logging
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.core.logging import log_config
from app.core.config import settings
from app.controllers.route import api_router
from app.utils.user import open_nickname_csv, make_nickname_list, nicknames

dictConfig(log_config)
logger = logging.getLogger('ddakkm_logger')

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


# 실제 IP 로깅
@app.middleware("http")
async def log_real_ip(request: Request, call_next):
    response = await call_next(request)
    real_ip = request.headers.get("x-real-ip", None)
    if real_ip:
        logger.info(f"[{request.method.upper()}] -> {request.url} FROM : {real_ip} \n ======= \n ")
    return response


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