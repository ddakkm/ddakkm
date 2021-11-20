from typing import List
import os

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365

    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    BOTO3_REGION: str
    BOTO3_ACCESS_KEY: str
    BOTO3_SECRET_KEY: str

    FCM_API_KEY: str

    TEST_USER_ID: str
    TEST_USER_PW: str

# debug
# _env_file=f'{os.getenv("app_env", "../app/env/local")}.env'

# normal
_env_file=f'{os.getenv("app_env", "../env/local")}.env'

settings = Settings(_env_file=_env_file)
