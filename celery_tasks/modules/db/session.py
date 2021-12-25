import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .. import const

env = os.getenv("ENVIRONMENT", "prod")

if env == "dev":
    database_uri = f"mysql+pymysql://{const.DEV_MYSQL_USER}:{const.DEV_MYSQL_PASSWORD}@{const.DEV_MYSQL_SERVER}:3306" \
                   f"/{const.DEV_MYSQL_DB}?charset=utf8mb4"
else:
    database_uri = f"mysql+pymysql://{const.PROD_MYSQL_USER}:{const.PROD_MYSQL_PASSWORD}@{const.PROD_MYSQL_SERVER}:3306" \
                   f"/{const.PROD_MYSQL_DB}?charset=utf8mb4"

engine = create_engine(database_uri, pool_pre_ping=True, pool_size=15, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)