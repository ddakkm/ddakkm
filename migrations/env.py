import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import pymysql
from alembic import context

pymysql.install_as_MySQLdb()

_env_file = f'{os.getenv("app_env", "./app/env/local")}.env'

load_dotenv(dotenv_path=_env_file)
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_HOST = os.environ.get("MYSQL_SERVER")
MYSQL_PASS = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB = os.environ.get("MYSQL_DB")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# alemic.ini 에 SQL 경로가 지정되어있지 않으면, 환경변수에서 SQL 연동 정보 가져와 덮어씌움
if not config.get_main_option('sqlalchemy.url'):
    config.set_main_option('sqlalchemy.url', f'mysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:3306/{MYSQL_DB}?charset=utf8mb4')

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# alembic이 auto generate 하기 위한 모델 구조에 대한 Metadata 제공
from app import models

target_metadata = models.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
