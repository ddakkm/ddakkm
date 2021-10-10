from typing import List
import os

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    API_ADMIN_STR: str = "/admin"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365
    SERVER_NAME: str = "ddakkm_api"
    SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str
    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

# debug
# _env_file=f'{os.getenv("app_env", "../app/env/local")}.env'

# normal
_env_file=f'{os.getenv("app_env", "../env/local")}.env'
settings = Settings(_env_file=_env_file)
